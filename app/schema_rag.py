import re

# Domain knowledge + schema descriptions
SCHEMA_DOCS = [
    {
        "id": "chambers",
        "keywords": ["chamber", "location", "capacity", "zone"],
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
        "keywords": [
            "capacity", "used", "usage", "utilization",
            "highest", "lowest", "maximum", "minimum",
            "month", "today", "days"
        ],
        "content": """Table: capacity_logs
Daily capacity utilization log.
Columns:
- chamber_id → chambers.id
- log_date: date of the record
- used_capacity_cbm: how much capacity was used that day
- total_capacity_cbm: total capacity of that chamber
- utilization_pct: (used/total)*100
This is the MAIN table for capacity related questions."""
    },
    {
        "id": "inventory_snapshots",
        "keywords": [
            "inventory", "stock", "quantity",
            "product", "snapshot"
        ],
        "content": """Table: inventory_snapshots
Point-in-time inventory.
Columns:
- chamber_id, product_id, quantity,
  snapshot_date, used_capacity_cbm
Join with products and chambers for stock questions."""
    },
    {
        "id": "products",
        "keywords": [
            "product", "sku", "name",
            "category", "volume"
        ],
        "content": """Table: products
Columns:
- sku
- name
- category
- volume_cbm (volume of one unit)"""
    },
    {
        "id": "capacity_calc",
        "keywords": [
            "calculation", "utilization",
            "highest", "lowest", "maximum",
            "minimum", "used", "capacity"
        ],
        "content": """Capacity Calculation Rules:
utilization_pct = (used_capacity_cbm / total_capacity_cbm) * 100
"this month" means current calendar month
"last month" means previous calendar month
"sabse zyada" / "highest" / "maximum"
→ ORDER BY utilization_pct DESC or used_capacity_cbm DESC
Always join capacity_logs with chambers on chamber_id."""
    },
    {
        "id": "example_queries",
        "keywords": [
            "example", "chamber", "month",
            "highest", "lowest"
        ],
        "content": """Example natural language → SQL:
Q: kaunse chamber me is month sabse zyada capacity used hui?
→ SELECT c.name, AVG(cl.utilization_pct) as avg_util
FROM capacity_logs cl
JOIN chambers c ON cl.chamber_id = c.id
WHERE strftime('%Y-%m', cl.log_date) =
      strftime('%Y-%m', 'now')
GROUP BY c.name
ORDER BY avg_util DESC
LIMIT 1;"""
    }
]


class SchemaRAG:
    def __init__(self):
        self.documents = SCHEMA_DOCS

    def retrieve(self, query: str, k: int = 4) -> str:
        query_words = set(re.findall(r"\w+", query.lower()))

        scored_docs = []

        for doc in self.documents:
            score = len(query_words.intersection(doc["keywords"]))
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        selected = [
            doc["content"]
            for score, doc in scored_docs[:k]
            if score > 0
        ]

        # If nothing matched, return general schema context
        if not selected:
            selected = [doc["content"] for doc in self.documents[:k]]

        return "\n\n---\n\n".join(selected)


schema_rag = SchemaRAG()