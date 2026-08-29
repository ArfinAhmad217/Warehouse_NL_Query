from fastapi import FastAPI, HTTPException, Depends
from app.auth import router as auth_router, get_current_user
from app.models import QueryRequest, QueryResponse
from app.sql_agent import generate_sql, is_safe_sql, execute_sql
from app.database import init_db
from contextlib import asynccontextmanager
from openai import OpenAI
from app.config import settings
from app.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()          # create tables + seed data
    yield

app = FastAPI(
    title="Warehouse NL Query Assistant",
    description="Text-to-SQL + RAG hybrid for Warehouse Capacity & Inventory",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

def generate_natural_answer(question: str, sql: str, result: dict) -> str:
    """Optional: LLM se natural language answer banao"""
    prompt = f"""User asked: {question}
Generated SQL: {sql}
Result: {result}

Give a short, clear answer in simple Hindi + English mix (jaise user ne poocha)."""
    resp = client.chat.completions.create(
        model=settings.MODEL_NAME,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

@app.post("/query", response_model=QueryResponse)
def query_warehouse(req: QueryRequest, current_user=Depends(get_current_user)):
    try:
        sql = generate_sql(req.question)

        if not is_safe_sql(sql):
            raise HTTPException(status_code=400, detail="Unsafe SQL generated. Only SELECT allowed.")

        result = execute_sql(sql)
        answer = generate_natural_answer(req.question, sql, result)

        return QueryResponse(
            question=req.question,
            generated_sql=sql,
            result=result,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "Warehouse Natural Language Query Assistant is running 🚀",
        "example": "POST /query  →  {\"question\": \"kaunse chamber me is month sabse zyada capacity used hui?\"}"
    }