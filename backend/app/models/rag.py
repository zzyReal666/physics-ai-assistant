from __future__ import annotations

from pydantic import BaseModel, Field


class RagRetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RagRetrieveChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    content: str
    score: float
    vector_score: float
    lexical_score: float
