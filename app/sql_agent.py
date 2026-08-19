from openai import OpenAI
from app.config import settings
from app.schema_rag import schema_rag
from sqlalchemy import text
from app.database import engine
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

SYSTEM_PROMPT = """You are an expert Text-to-SQL assistant for a Warehouse Inventory system.
You only generate **read-only SELECT** queries for SQLite.

Rules:
1. Use ONLY the tables and columns provided in the context.
2. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
3. Prefer utilization_pct for "capacity used" questions.
4. For "this month" use: strftime('%Y-%m', log_date) = strftime('%Y-%m', 'now')
5. For "last month": strftime('%Y-%m', log_date) = strftime('%Y-%m', date('now', '-1 month'))
6. Always JOIN chambers when chamber name is needed.
7. Return ONLY the SQL query. No explanation, no markdown, no ```.

Relevant schema + domain knowledge:
{context}
"""

def generate_sql(question: str) -> str:
    context = schema_rag.retrieve(question)
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question}
        ]
    )
    sql = response.choices[0].message.content.strip()
    # clean markdown if any
    sql = re.sub(r"```sql|```", "", sql).strip()
    return sql

def is_safe_sql(sql: str) -> bool:
    sql_lower = sql.lower().strip()
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "replace", "grant"]
    if any(f in sql_lower for f in forbidden):
        return False
    if not sql_lower.startswith("select"):
        return False
    return True

def execute_sql(sql: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}