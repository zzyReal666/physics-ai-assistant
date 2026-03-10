"""Pydantic request/response models.

说明：
- 将路由中的数据模型独立出来，便于复用与单元测试。
- 也便于你学习“接口层(routers) 与 数据契约层(models)”分离。
"""

from .chat import ChatAnswer, ChatRequest
from .document import (
    DeleteDocumentResponse,
    DocumentChunk,
    DocumentDetail,
    DocumentItem,
    ReprocessDocumentResponse,
    UploadDocumentResponse,
)
from .exam import (
    ExamGenerateRequest,
    ExamGenerateResponse,
    ExamListItem,
    ExamQuestion,
)
from .rag import RagRetrieveChunk, RagRetrieveRequest
from .settings import ModelConfigResponse, ModelConfigUpdateRequest, ProviderStatus
from .teaching import TeachingPlanRequest, TeachingPlanResponse

__all__ = [
    'ChatAnswer',
    'ChatRequest',
    'DeleteDocumentResponse',
    'DocumentChunk',
    'DocumentDetail',
    'DocumentItem',
    'ExamGenerateRequest',
    'ExamGenerateResponse',
    'ExamListItem',
    'ExamQuestion',
    'ModelConfigResponse',
    'ModelConfigUpdateRequest',
    'ProviderStatus',
    'RagRetrieveChunk',
    'RagRetrieveRequest',
    'ReprocessDocumentResponse',
    'TeachingPlanRequest',
    'TeachingPlanResponse',
    'UploadDocumentResponse',
]
