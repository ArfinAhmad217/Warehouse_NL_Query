import chromadb
from chromadb.utils import embedding_functions
from app.config import settings
import os

# Domain knowledge + schema descriptions (yehi RAG ka asli power hai)
SCHEMA_DOCS = [
    {
        "id": "chambers",
        "content": """Table: chambers
Columns:
- id (PK)
- name: Chamber name like CH-01, CH-02
- location: Zone A / Zone B / Zone C
- total_capacity_cbm: Total storage capacity in cubic meters
- is_active: true/false
Use this table when asking about chambers, their location or total capacity."""
    },
    {
        "id": "capacity_logs",
        "content": """Table: capacity_logs
Daily capacity utilization log.
Columns:
- chamber_id → chambers.id
- log_date: date of the record
- used_capacity_cbm: how much capacity was used that day
- total_capacity_cbm: total capacity of that chamber
- utilization_pct: (used/total)*100
This is the MAIN table for capacity related questions like "sabse zyada capacity used", "highest utilization", "this month capacity" etc."""
    },
    {
        "id": "inventory_snapshots",
        "content": """Table: inventory_snapshots
Point-in-time inventory.
Columns:
- chamber_id, product_id, quantity, snapshot_date, used_capacity_cbm
Join with products and chambers for stock questions."""
    },
    {
        "id": "products",
        "content": """Table: products
- sku, name, category, volume_cbm (volume of one unit)"""
    },
    {
        "id": "capacity_calc",
        "content": """Capacity Calculation Rules (from previous warehouse survey system):
utilization_pct = (used_capacity_cbm / total_capacity_cbm) * 100
"this month" means current calendar month
"last month" means previous calendar month
"sabse zyada" / "highest" / "maximum" → ORDER BY utilization_pct DESC or used_capacity_cbm DESC
Always join capacity_logs with chambers on chamber_id to get chamber name."""
    },
    {
        "id": "example_queries",
        "content": """Example natural language → SQL patterns:
Q: kaunse chamber me is month sabse zyada capacity used hui?
→ SELECT c.name, AVG(cl.utilization_pct) as avg_util
  FROM capacity_logs cl JOIN chambers c ON cl.chamber_id = c.id
  WHERE strftime('%Y-%m', cl.log_date) = strftime('%Y-%m', 'now')
  GROUP BY c.name ORDER BY avg_util DESC LIMIT 1;

Q: last 7 days me kis chamber ki capacity sabse kam use hui?
→ similar with date filter and ORDER BY ASC"""
    }
]

class SchemaRAG:
    def __init__(self):
        os.makedirs(settings.CHROMA_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name="warehouse_schema",
            embedding_function=self.ef
        )
        self._load_docs()

    def _load_docs(self):
        if self.collection.count() > 0:
            return
        self.collection.add(
            documents=[d["content"] for d in SCHEMA_DOCS],
            ids=[d["id"] for d in SCHEMA_DOCS]
        )
        print("✅ Schema RAG loaded")

    def retrieve(self, query: str, k: int = 4) -> str:
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results["documents"][0]
        return "\n\n---\n\n".join(docs)

schema_rag = SchemaRAG()