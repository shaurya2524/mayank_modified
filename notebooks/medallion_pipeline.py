# Databricks notebook source
# Read the CSV from your Volume
bns_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/legal_catalog/nyaya_sahayak/ipc/bns_sections.csv")

# Clean column names (strip spaces, replaces with underscores)
for col in bns_df.columns:
    bns_df = bns_df.withColumnRenamed(col, col.strip().replace(" ", "_"))

# Save as a permanent Delta Table
bns_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.bns_main")

print("✅ BNS Main Table Created!")


# COMMAND ----------

# MAGIC %pip install pdfplumber
# MAGIC

# COMMAND ----------

import pdfplumber
import io

pdf_path = "/Volumes/legal_catalog/nyaya_sahayak/ipc/250883_english_01042024.pdf"

# Extract text from PDF
with pdfplumber.open(pdf_path) as pdf:
    full_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Create a simple single-row table with the full text for now
spark.createDataFrame([(full_text,)], ["raw_text"]) \
    .write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.ipc_raw_text")

print("✅ IPC Raw Text Saved to Delta!")


# COMMAND ----------

import pdfplumber
import io

repealed_path = "/Volumes/legal_catalog/nyaya_sahayak/ipc/repealedfileopen.pdf"

with pdfplumber.open(repealed_path) as pdf:
    # We extract this into a separate table so the AI can specifically check 
    # if an old law still exists or has been repealed.
    repealed_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

spark.createDataFrame([(repealed_text,)], ["repealed_context"]) \
    .write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.ipc_repealed_reference")

print("✅ Repealed Provisions Table Created!")


# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM legal_catalog.nyaya_sahayak.bns_main LIMIT 10;
# MAGIC

# COMMAND ----------

import re
from pyspark.sql.functions import udf, explode, concat_ws, col
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType, StringType

# ==========================================
# 1. DEFINE THE PARSING UDF FOR PDF TEXT
# ==========================================
def _parse_ipc(text_blob):
    pattern = re.compile(
        r'(?:^|\n)(?:Section\s+)?(\d{1,3}[A-Z]?)\.?\s+([^\n]{3,80})\n([\s\S]*?)(?=(?:\n(?:Section\s+)?\d{1,3}[A-Z]?\.?\s)|$)',
        re.MULTILINE)
    sections = []
    
    if not text_blob:
        return sections
        
    for m in pattern.finditer(text_blob):
        label = m.group(1).strip()
        name  = m.group(2).strip()
        desc  = m.group(3).strip()[:2000]
        try: 
            num = int(re.sub(r'[A-Z]','',label))
        except: 
            num = 0
            
        if desc and len(name) > 3:
            # Combine name and description so the AI embeds the full context
            full_content = f"Section {label} - {name}\n{desc}"
            sections.append((num, label, name, full_content))
    return sections

# Register the Python function as a Spark UDF
schema = ArrayType(StructType([
    StructField("section_num", IntegerType(), True),
    StructField("section_label", StringType(), True),
    StructField("section_name", StringType(), True),
    StructField("content", StringType(), True)
]))
parse_ipc_udf = udf(_parse_ipc, schema)

# ==========================================
# 2. PROCESS MAIN IPC TABLE
# ==========================================
raw_ipc_df = spark.table("legal_catalog.nyaya_sahayak.ipc_raw_text")

structured_ipc = raw_ipc_df.withColumn("parsed", parse_ipc_udf("raw_text")) \
                           .select(explode("parsed").alias("section")) \
                           .select("section.*")

# Drop any existing table and create new Gold table with Change Data Feed enabled
spark.sql("DROP TABLE IF EXISTS legal_catalog.nyaya_sahayak.ipc_gold")
structured_ipc.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.ipc_gold")

print("✅ Structured IPC Gold Table Created!")

# ==========================================
# 3. PROCESS REPEALED IPC TABLE
# ==========================================
raw_repealed_df = spark.table("legal_catalog.nyaya_sahayak.ipc_repealed_reference")

structured_repealed = raw_repealed_df.withColumn("parsed", parse_ipc_udf("repealed_context")) \
                                     .select(explode("parsed").alias("section")) \
                                     .select("section.*")

# Drop any existing table and create new Gold table with Change Data Feed enabled
spark.sql("DROP TABLE IF EXISTS legal_catalog.nyaya_sahayak.repealed_gold")
structured_repealed.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.repealed_gold")

print("✅ Structured Repealed Gold Table Created!")

# ==========================================
# 4. PROCESS BNS TABLE (CORRECTED COLUMNS)
# ==========================================
from pyspark.sql.functions import concat_ws, col

bns_df = spark.table("legal_catalog.nyaya_sahayak.bns_main")

# We map exactly to the columns existing in your base table: 
# 'Section__name', 'Section', 'Chapter_name', 'Description'
bns_gold = bns_df.withColumn("content", 
    concat_ws("\n", 
              col("Chapter_name"), 
              col("Section__name"), 
              col("Description"))
)

# Rename the 'Section' column to 'section_num' so the primary key matches across all 3 tables
bns_gold = bns_gold.withColumnRenamed("Section", "section_num")

# Select final columns to match the clean schema
bns_gold = bns_gold.select("section_num", "Chapter_name", "Section__name", "content")

# Drop any existing table and create new Gold table with Change Data Feed enabled
spark.sql("DROP TABLE IF EXISTS legal_catalog.nyaya_sahayak.bns_gold")
bns_gold.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.bns_gold")

print("✅ BNS Gold Table Created successfully!")

print("🚀 All three Gold tables are fully structured and ready for Vector Indexing.")


# COMMAND ----------

# ==========================================
# 5. PROCESS SCHEMES TABLE (data.parquet)
# ==========================================
# Upload data.parquet to:
#   /Volumes/legal_catalog/nyaya_sahayak/schemes/data.parquet
# before running this cell.

from pyspark.sql.functions import concat_ws, col, coalesce, lit

schemes_raw = spark.read.parquet(
    "/Volumes/legal_catalog/nyaya_sahayak/schemes/data.parquet"
)

# Drop junk column if present
if "Unnamed: 9" in schemes_raw.columns:
    schemes_raw = schemes_raw.drop("Unnamed: 9")

# Build a rich content column for vector embedding:
# scheme_name + eligibility + benefits + category + tags
schemes_gold = schemes_raw.withColumn(
    "content",
    concat_ws(
        "\n",
        coalesce(col("scheme_name"), lit("")),
        coalesce(col("eligibility"),  lit("")),
        coalesce(col("benefits"),     lit("")),
        coalesce(col("schemeCategory"), lit("")),
        coalesce(col("tags"),         lit("")),
    )
).select(
    "scheme_name",
    "slug",
    "benefits",
    "eligibility",
    "application",
    "schemeCategory",
    "level",
    "tags",
    "content",      # ← embedded by vector search
)

spark.sql("DROP TABLE IF EXISTS legal_catalog.nyaya_sahayak.schemes_gold")
schemes_gold.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("overwrite") \
    .saveAsTable("legal_catalog.nyaya_sahayak.schemes_gold")

print(f"✅ Schemes Gold Table Created! ({schemes_gold.count()} schemes)")
print("🚀 Now create a Mosaic AI Vector Search index on 'content' column via the Databricks UI or SDK.")
