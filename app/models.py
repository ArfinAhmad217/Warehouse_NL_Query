from pydantic import BaseModel
from typing import Any, List, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    generated_sql: str
    result: dict
    answer: Optional[str] = None