from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.dependencies import get_document_store, get_rag_service
from app.models import (
    DeleteDocumentResponse,
    DocumentDetail,
    DocumentItem,
    ReprocessDocumentResponse,
    UploadDocumentResponse,
)
from app.services.document_store import DocumentStore
from app.services.rag_service import RagService


router = APIRouter()


@router.post("/upload", response_model=UploadDocumentResponse, summary="上传文档")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    store: DocumentStore = Depends(get_document_store),
    rag_service: RagService = Depends(get_rag_service),
) -> UploadDocumentResponse:
    """上传文档并异步入索引。

    这是 RAG 链路的起点：
    1) 接收文件并落盘；
    2) 快速返回 `uploaded`（不等待重任务）；
    3) 后台任务完成解析、分块、向量化、入索引。
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容不能为空")

    try:
        result = await store.upload(file.filename, content)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    # FastAPI BackgroundTasks 会在响应返回后执行，不阻塞主请求。
    background_tasks.add_task(store.process_document, result.document_id, rag_service, 2)

    return UploadDocumentResponse(
        document_id=result.document_id,
        filename=result.filename,
        status=result.status,
        message=result.message,
    )


@router.post(
    "/{document_id}/reprocess",
    response_model=ReprocessDocumentResponse,
    summary="重建文档索引",
)
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    store: DocumentStore = Depends(get_document_store),
    rag_service: RagService = Depends(get_rag_service),
) -> ReprocessDocumentResponse:
    """手动重建索引。

    常见场景：
    - 你升级了分块策略或 embedding 模型；
    - 某文档历史处理失败，需要重新处理。
    """
    doc = await store.get_document_meta(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    background_tasks.add_task(store.process_document, document_id, rag_service, 2)
    return ReprocessDocumentResponse(success=True, message="已提交重建任务")


@router.get("/", response_model=list[DocumentItem], summary="文档列表")
async def list_documents(
    store: DocumentStore = Depends(get_document_store),
) -> list[DocumentItem]:
    """文档列表（含状态字段，便于前端做处理中/失败提示）。"""
    docs = await store.list_documents()
    return [DocumentItem(**doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentDetail, summary="文档详情")
async def get_document(
    document_id: str,
    store: DocumentStore = Depends(get_document_store),
) -> DocumentDetail:
    """文档详情（含实时分块预览）。"""
    doc = await store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentDetail(**doc)


@router.delete("/{document_id}", response_model=DeleteDocumentResponse, summary="删除文档")
async def delete_document(
    document_id: str,
    store: DocumentStore = Depends(get_document_store),
    rag_service: RagService = Depends(get_rag_service),
) -> DeleteDocumentResponse:
    """删除文档：文件、元数据、RAG 索引三者一起清理。"""
    ok = await store.delete_document(document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="文档不存在")
    await rag_service.remove_document(document_id)
    return DeleteDocumentResponse(success=True, message="文档已删除")
