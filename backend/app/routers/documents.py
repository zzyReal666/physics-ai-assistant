from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.dependencies import get_document_store
from app.services.document_store import DocumentStore


router = APIRouter()


class UploadDocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: Literal["processed"]
    message: str


class DocumentItem(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: str


class DocumentChunk(BaseModel):
    index: str
    content: str


class DocumentDetail(DocumentItem):
    stored_filename: str
    chunks: list[DocumentChunk]
    chunk_count: int


class DeleteDocumentResponse(BaseModel):
    success: bool
    message: str


@router.post("/upload", response_model=UploadDocumentResponse, summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    store: DocumentStore = Depends(get_document_store),
) -> UploadDocumentResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容不能为空")

    try:
        result = await store.upload(file.filename, content)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    return UploadDocumentResponse(
        document_id=result.document_id,
        filename=result.filename,
        status=result.status,
        message=result.message,
    )


@router.get("/", response_model=list[DocumentItem], summary="文档列表")
async def list_documents(
    store: DocumentStore = Depends(get_document_store),
) -> list[DocumentItem]:
    docs = await store.list_documents()
    return [DocumentItem(**doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentDetail, summary="文档详情")
async def get_document(
    document_id: str,
    store: DocumentStore = Depends(get_document_store),
) -> DocumentDetail:
    doc = await store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentDetail(**doc)


@router.delete("/{document_id}", response_model=DeleteDocumentResponse, summary="删除文档")
async def delete_document(
    document_id: str,
    store: DocumentStore = Depends(get_document_store),
) -> DeleteDocumentResponse:
    ok = await store.delete_document(document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DeleteDocumentResponse(success=True, message="文档已删除")
