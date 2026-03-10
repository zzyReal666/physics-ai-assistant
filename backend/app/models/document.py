from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: Literal['uploaded', 'processing', 'processed', 'failed']
    message: str


class DocumentItem(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    retry_count: int = 0
    last_error: str | None = None
    chunk_count: int = 0
    created_at: str


class DocumentChunk(BaseModel):
    index: str
    content: str


class DocumentDetail(DocumentItem):
    stored_filename: str
    chunks: list[DocumentChunk]


class DeleteDocumentResponse(BaseModel):
    success: bool
    message: str


class ReprocessDocumentResponse(BaseModel):
    success: bool
    message: str
