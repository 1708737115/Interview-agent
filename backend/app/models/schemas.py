from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class InterviewMode(str, Enum):
    STRUCTURED = "structured"
    OPEN = "open"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TXT = "txt"


class DocumentUploadRequest(BaseModel):
    title: str = Field(..., description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")


class DocumentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    file_type: DocumentType
    status: str
    created_at: datetime
    chunk_count: int = 0


class StartInterviewRequest(BaseModel):
    mode: InterviewMode = Field(default=InterviewMode.STRUCTURED, description="面试模式")
    knowledge_base_ids: List[str] = Field(default=[], description="使用的知识库ID列表")
    candidate_info: Optional[str] = Field(None, description="候选人背景信息（开放式面试用）")
    duration_minutes: int = Field(default=30, ge=10, le=120, description="面试时长（分钟）")


class InterviewSession(BaseModel):
    id: str
    mode: InterviewMode
    status: str
    current_question_index: int = 0
    total_questions: int
    started_at: datetime
    ended_at: Optional[datetime] = None


class QuestionResponse(BaseModel):
    id: str
    question: str
    question_type: str
    difficulty: int = Field(..., ge=1, le=5)
    context: Optional[str] = None


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class EvaluationDimension(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    feedback: str


class AnswerResponse(BaseModel):
    evaluation: List[EvaluationDimension]
    total_score: float
    feedback: str
    suggestions: List[str]
    next_question: Optional[QuestionResponse] = None


class InterviewReport(BaseModel):
    session_id: str
    mode: InterviewMode
    total_questions: int
    average_score: float
    dimensions_summary: List[EvaluationDimension]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    generated_at: datetime


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    message: str
    retrieved_contexts: Optional[List[str]] = None
