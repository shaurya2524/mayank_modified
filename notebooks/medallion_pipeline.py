# Databricks notebook source
# MAGIC %md
# MAGIC # Nyaya-Sahayak — One-Click Setup
# MAGIC
# MAGIC **Just clone this repo into Databricks and click "Run All" on this notebook.**
# MAGIC
# MAGIC This notebook will:
# MAGIC 0. (One-time only) Set up the Sarvam API Secret — see Step 0 below
# MAGIC 1. Create catalog `legal_catalog` + schema `nyaya_sahayak` + required Volumes
# MAGIC 2. Copy data files from the cloned repo into the Volumes
# MAGIC 3. Build all four Gold-layer Delta tables with Change Data Feed enabled
# MAGIC 4. Create a Mosaic AI Vector Search endpoint
# MAGIC 5. Create three Vector Search indexes (`bns_gold_index`, `ipc_gold_index`, `schemes_gold_index`)
# MAGIC
# MAGIC After this finishes, the Streamlit app is ready to deploy via **Compute → Apps**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0 — Sarvam API Key
# MAGIC
# MAGIC The key is already inlined in `app.yaml`. Nothing to do here — the cell below just verifies it's accessible.

# COMMAND ----------

import os
print("Sarvam key visible to notebook env:", bool(os.environ.get("sarvam_api_key", "")))

# COMMAND ----------

# MAGIC %pip install pdfplumber databricks-vectorsearch
# MAGIC %restart_python

# COMMAND ----------

# ==========================================================================
# 0. CONFIG & PATH RESOLUTION
# ==========================================================================
import os, glob

CATALOG  = "legal_catalog"
SCHEMA   = "nyaya_sahayak"
ENDPOINT = "nyaya_sahayak_endpoint"

# Try multiple ways to find the repo root, since Databricks paths vary
# by workspace setup (Repos vs. Workspace, with/without /Workspace prefix).
def _find_repo_root():
    candidates = []

    # 1. From notebook context
    try:
        nb_path = (
            dbutils.notebook.entry_point.getDbutils().notebook()
            .getContext().notebookPath().get()
        )
        # nb_path is like /Repos/user/repo/notebooks/medallion_pipeline
        repo_relative = os.path.dirname(os.path.dirname(nb_path))
        candidates += [
            "/Workspace" + repo_relative,
            repo_relative,
        ]
    except Exception as e:
        print(f"  notebook context: {e}")

    # 2. From CWD
    cwd = os.getcwd()
    candidates += [cwd, os.path.dirname(cwd)]

    # 3. Scan /Workspace/Repos for any folder containing bns_sections.csv
    for hit in glob.glob("/Workspace/Repos/*/*/bns_sections.csv"):
        candidates.append(os.path.dirname(hit))
    for hit in glob.glob("/Workspace/Users/*/*/bns_sections.csv"):
        candidates.append(os.path.dirname(hit))

    for c in candidates:
        marker = os.path.join(c, "bns_sections.csv")
        if os.path.exists(marker):
            return c

    raise RuntimeError(
        "Could not find repo root containing bns_sections.csv.\n"
        f"Searched: {candidates}\n"
        "Make sure this notebook is run from inside a cloned Databricks Repo."
    )

REPO_ROOT_WS = _find_repo_root()
print(f"📁 Repo root resolved to: {REPO_ROOT_WS}")
print(f"   Files there: {os.listdir(REPO_ROOT_WS)[:6]} ...")

VOL_IPC     = f"/Volumes/{CATALOG}/{SCHEMA}/ipc"
VOL_SCHEMES = f"/Volumes/{CATALOG}/{SCHEMA}/schemes"

# COMMAND ----------

# ==========================================================================
# 1. CREATE CATALOG, SCHEMA, AND VOLUMES (idempotent)
# ==========================================================================
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA  IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME  IF NOT EXISTS {CATALOG}.{SCHEMA}.ipc")
spark.sql(f"CREATE VOLUME  IF NOT EXISTS {CATALOG}.{SCHEMA}.schemes")
print("✅ Catalog, schema, and volumes ready.")

# COMMAND ----------

# ==========================================================================
# 2. COPY DATA FILES FROM REPO → VOLUMES (using dbutils.fs for reliability)
# ==========================================================================
FILES_TO_COPY = [
    (f"{REPO_ROOT_WS}/bns_sections.csv",            f"{VOL_IPC}/bns_sections.csv"),
    (f"{REPO_ROOT_WS}/250883_english_01042024.pdf", f"{VOL_IPC}/250883_english_01042024.pdf"),
    (f"{REPO_ROOT_WS}/repealedfileopen.pdf",        f"{VOL_IPC}/repealedfileopen.pdf"),
    (f"{REPO_ROOT_WS}/data.parquet",                f"{VOL_SCHEMES}/data.parquet"),
]

for src, dst in FILES_TO_COPY:
    if not os.path.exists(src):
        print(f"❌ Missing source: {src}")
        continue
    try:
        dbutils.fs.cp(f"file:{src}", dst, recurse=False)
        print(f"✅ {os.path.basename(src)}  →  {dst}")
    except Exception as e1:
        # Fallback: read bytes and write via dbutils.fs.put or shutil
        try:
            import shutil
            shutil.copy2(src, dst)
            print(f"✅ (shutil) {os.path.basename(src)}  →  {dst}")
        except Exception as e2:
            print(f"❌ Both copy methods failed for {src}:\n  dbutils.fs: {e1}\n  shutil:    {e2}")

# Verify
print("\nVolume contents:")
for vol in (VOL_IPC, VOL_SCHEMES):
    try:
        print(f"  {vol}: {os.listdir(vol)}")
    except Exception as e:
        print(f"  {vol}: <unable to list — {e}>")

# COMMAND ----------

# ==========================================================================
# 3. INGEST BNS — Bronze
# ==========================================================================
bns_df = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(f"{VOL_IPC}/bns_sections.csv")
)
for c in bns_df.columns:
    bns_df = bns_df.withColumnRenamed(c, c.strip().replace(" ", "_"))

bns_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.bns_main")
print("✅ BNS Main Table Created.")

# COMMAND ----------

# ==========================================================================
# 4. INGEST IPC PDFs (main + repealed) — Bronze
# ==========================================================================
import pdfplumber

def _pdf_to_text(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

ipc_text      = _pdf_to_text(f"{VOL_IPC}/250883_english_01042024.pdf")
repealed_text = _pdf_to_text(f"{VOL_IPC}/repealedfileopen.pdf")

(spark.createDataFrame([(ipc_text,)], ["raw_text"])
 .write.format("delta").mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.ipc_raw_text"))
print("✅ IPC raw text saved.")

(spark.createDataFrame([(repealed_text,)], ["repealed_context"])
 .write.format("delta").mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.ipc_repealed_reference"))
print("✅ Repealed IPC raw text saved.")

# COMMAND ----------

# ==========================================================================
# 5. PARSE IPC SECTIONS (UDF) — Silver / Gold
# ==========================================================================
import re
from pyspark.sql.functions import udf, explode, concat_ws, col, coalesce, lit
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType, StringType

def _parse_ipc(text_blob):
    pattern = re.compile(
        r'(?:^|\n)(?:Section\s+)?(\d{1,3}[A-Z]?)\.?\s+([^\n]{3,80})\n([\s\S]*?)(?=(?:\n(?:Section\s+)?\d{1,3}[A-Z]?\.?\s)|$)',
        re.MULTILINE,
    )
    out = []
    if not text_blob:
        return out
    for m in pattern.finditer(text_blob):
        label = m.group(1).strip()
        name  = m.group(2).strip()
        desc  = m.group(3).strip()[:2000]
        try:    num = int(re.sub(r'[A-Z]', '', label))
        except: num = 0
        if desc and len(name) > 3:
            out.append((num, label, name, f"Section {label} - {name}\n{desc}"))
    return out

schema = ArrayType(StructType([
    StructField("section_num",   IntegerType()),
    StructField("section_label", StringType()),
    StructField("section_name",  StringType()),
    StructField("content",       StringType()),
]))
parse_ipc_udf = udf(_parse_ipc, schema)

# IPC Gold
raw_ipc = spark.table(f"{CATALOG}.{SCHEMA}.ipc_raw_text")
ipc_gold = (
    raw_ipc.withColumn("parsed", parse_ipc_udf("raw_text"))
           .select(explode("parsed").alias("section"))
           .select("section.*")
)
spark.sql(f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.ipc_gold")
(ipc_gold.write.format("delta")
 .option("delta.enableChangeDataFeed", "true")
 .mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.ipc_gold"))
print(f"✅ ipc_gold created ({ipc_gold.count()} sections).")

# Repealed Gold
raw_rep = spark.table(f"{CATALOG}.{SCHEMA}.ipc_repealed_reference")
rep_gold = (
    raw_rep.withColumn("parsed", parse_ipc_udf("repealed_context"))
           .select(explode("parsed").alias("section"))
           .select("section.*")
)
spark.sql(f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.repealed_gold")
(rep_gold.write.format("delta")
 .option("delta.enableChangeDataFeed", "true")
 .mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.repealed_gold"))
print(f"✅ repealed_gold created ({rep_gold.count()} sections).")

# COMMAND ----------

# ==========================================================================
# 6. BNS GOLD
# ==========================================================================
bns_main = spark.table(f"{CATALOG}.{SCHEMA}.bns_main")

bns_gold = (
    bns_main.withColumn(
        "content",
        concat_ws("\n", col("Chapter_name"), col("Section__name"), col("Description")),
    )
    .withColumnRenamed("Section", "section_num")
    .select("section_num", "Chapter_name", "Section__name", "content")
)
spark.sql(f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.bns_gold")
(bns_gold.write.format("delta")
 .option("delta.enableChangeDataFeed", "true")
 .mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.bns_gold"))
print(f"✅ bns_gold created ({bns_gold.count()} sections).")

# COMMAND ----------

# ==========================================================================
# 7. SCHEMES GOLD (3,400+ government schemes)
# ==========================================================================
schemes_raw = spark.read.parquet(f"{VOL_SCHEMES}/data.parquet")
if "Unnamed: 9" in schemes_raw.columns:
    schemes_raw = schemes_raw.drop("Unnamed: 9")

schemes_gold = (
    schemes_raw
    .withColumn(
        "content",
        concat_ws(
            "\n",
            coalesce(col("scheme_name"),    lit("")),
            coalesce(col("eligibility"),    lit("")),
            coalesce(col("benefits"),       lit("")),
            coalesce(col("schemeCategory"), lit("")),
            coalesce(col("tags"),           lit("")),
        ),
    )
    .select("scheme_name", "slug", "benefits", "eligibility", "application",
            "schemeCategory", "level", "tags", "content")
)
spark.sql(f"DROP TABLE IF EXISTS {CATALOG}.{SCHEMA}.schemes_gold")
(schemes_gold.write.format("delta")
 .option("delta.enableChangeDataFeed", "true")
 .mode("overwrite")
 .saveAsTable(f"{CATALOG}.{SCHEMA}.schemes_gold"))
print(f"✅ schemes_gold created ({schemes_gold.count()} schemes).")

# COMMAND ----------

# ==========================================================================
# 8. CREATE VECTOR SEARCH ENDPOINT (waits for it to be ready)
# ==========================================================================
from databricks.vector_search.client import VectorSearchClient

vs = VectorSearchClient(disable_notice=True)

try:
    vs.create_endpoint(name=ENDPOINT, endpoint_type="STANDARD")
    print(f"✅ Endpoint '{ENDPOINT}' creation requested.")
except Exception as e:
    print(f"ℹ️  Endpoint exists or already provisioning: {e}")

print("⏳ Waiting for endpoint to become online (this can take 5-10 minutes on first run)...")
vs.wait_for_endpoint(name=ENDPOINT, timeout=900, verbose=True)
print(f"✅ Endpoint '{ENDPOINT}' is ONLINE.")

# COMMAND ----------

# ==========================================================================
# 9. CREATE THREE VECTOR SEARCH INDEXES (Delta Sync, auto-managed embeddings)
# ==========================================================================
INDEX_SPECS = [
    {
        "index": f"{CATALOG}.{SCHEMA}.bns_gold_index",
        "table": f"{CATALOG}.{SCHEMA}.bns_gold",
        "pk":    "section_num",
    },
    {
        "index": f"{CATALOG}.{SCHEMA}.ipc_gold_index",
        "table": f"{CATALOG}.{SCHEMA}.ipc_gold",
        "pk":    "section_num",
    },
    {
        "index": f"{CATALOG}.{SCHEMA}.schemes_gold_index",
        "table": f"{CATALOG}.{SCHEMA}.schemes_gold",
        "pk":    "slug",
    },
]

# IPC table needs a primary key — make sure it's there. We add a synthetic one if not.
try:
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.bns_gold ALTER COLUMN section_num SET NOT NULL")
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.bns_gold ADD CONSTRAINT bns_pk PRIMARY KEY (section_num)")
except Exception as e:
    print(f"ℹ️  bns_gold PK: {e}")

try:
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.ipc_gold ALTER COLUMN section_num SET NOT NULL")
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.ipc_gold ADD CONSTRAINT ipc_pk PRIMARY KEY (section_num)")
except Exception as e:
    print(f"ℹ️  ipc_gold PK: {e}")

try:
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.schemes_gold ALTER COLUMN slug SET NOT NULL")
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.schemes_gold ADD CONSTRAINT schemes_pk PRIMARY KEY (slug)")
except Exception as e:
    print(f"ℹ️  schemes_gold PK: {e}")

# Now create / sync indexes
for spec in INDEX_SPECS:
    try:
        vs.create_delta_sync_index(
            endpoint_name=ENDPOINT,
            index_name=spec["index"],
            source_table_name=spec["table"],
            pipeline_type="TRIGGERED",
            primary_key=spec["pk"],
            embedding_source_column="content",
            embedding_model_endpoint_name="databricks-bge-large-en",
        )
        print(f"✅ Created index: {spec['index']}")
    except Exception as e:
        # Already exists — trigger a sync instead
        try:
            vs.get_index(endpoint_name=ENDPOINT, index_name=spec["index"]).sync()
            print(f"♻️  Re-synced existing index: {spec['index']}")
        except Exception as e2:
            print(f"⚠️  {spec['index']}: {e2}")

print("\n🚀 SETUP COMPLETE. Vector indexes will finish syncing in the background.")
print("   Now go to Compute → Apps → Create App and connect this repo.")
