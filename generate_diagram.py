import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Function to draw a box
def draw_box(ax, x, y, width, height, title, text, color):
    box = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='black', facecolor=color, alpha=0.9)
    ax.add_patch(box)
    ax.text(x + width/2, y + height - 2, title, horizontalalignment='center', verticalalignment='top', fontsize=11, fontweight='bold', color='black')
    ax.text(x + width/2, y + height/2 - 1, text, horizontalalignment='center', verticalalignment='center', fontsize=10, color='black')

# Function to draw an arrow
def draw_arrow(ax, start_x, start_y, end_x, end_y, text="", rad=0.0):
    arrow = patches.FancyArrowPatch((start_x, start_y), (end_x, end_y), connectionstyle=f"arc3,rad={rad}", color='black', arrowstyle="->", mutation_scale=15, lw=1.5)
    ax.add_patch(arrow)
    if text:
        # Calculate midpoint for text
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        ax.text(mid_x, mid_y + 2, text, horizontalalignment='center', fontsize=9, fontweight='bold', color='#1f77b4', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

# Define components
# 1. User/UI
draw_box(ax, 2, 45, 18, 15, "Frontend UI", "Streamlit\nUser Queries,\nHindi/English Mode", "#ADD8E6")

# 2. Main App Logic
draw_box(ax, 30, 45, 20, 15, "RAG Orchestrator", "rag_engine.py\nContext Retrieval", "#90EE90")

# 3. LLM Model
draw_box(ax, 30, 75, 20, 15, "Sarvam AI (LLM)", "Multilingual Generation\nDirect API Auth", "#FFB6C1")

# 4. Databricks Vectors
draw_box(ax, 65, 45, 22, 15, "Mosaic AI Vector Search", "Serverless Endpoint\nHybrid Semantic Search", "#FFD700")

# 5. Databricks Delta Tables
draw_box(ax, 65, 15, 22, 15, "Delta Lake (Gold)", "bns_gold, ipc_gold\nChange Data Feed (CDF)", "#D3D3D3")

# 6. Fallback local
draw_box(ax, 30, 15, 20, 15, "Local Fallback", "PageIndex \n& Keyword Search", "#E6E6FA")

# Connecting Arrows
draw_arrow(ax, 20, 55, 30, 55, "Query Input")
draw_arrow(ax, 30, 50, 20, 50, "Streamed UI Response")

draw_arrow(ax, 50, 50, 65, 50, "Vector Query", rad=0.1)
draw_arrow(ax, 65, 55, 50, 55, "Matched Chunks", rad=0.1)

draw_arrow(ax, 76, 30, 76, 45, "Continuous Auto-Sync")

draw_arrow(ax, 38, 60, 38, 75, "RAG Context + Prompt")
draw_arrow(ax, 42, 75, 42, 60, "LLM Answer")

draw_arrow(ax, 40, 45, 40, 30, "Fallback (If DBx Offline)")

plt.title("Nyaya-Sahayak: Medallion Architecture & Hybrid RAG", fontsize=16, fontweight='bold', fontfamily='sans-serif')
plt.savefig('/home/svashistha/nayay-sahinta/nyaya_architecture.png', bbox_inches='tight', dpi=300)
print("Diagram generated and saved to /home/svashistha/nayay-sahinta/nyaya_architecture.png")
