"""
Job Schema - API Request/Response Models
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    GENERATING_JSON = "generating_json"
    RENDERING = "rendering"
    DONE = "done"
    FAILED = "failed"


class GenerateRequest(BaseModel):
    """POST /generate request body"""
    prompt: str = Field(..., min_length=1, max_length=5000, description="User prompt for PPT generation")
    template_id: str = Field(default="default", description="Template ID (reserved for future use)")
    language: str = Field(default="auto", description="Output language: auto, en, zh, etc.")
    density: Literal["sparse", "normal", "dense"] = Field(default="normal", description="Content density")


class GenerateResponse(BaseModel):
    """POST /generate response"""
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    """GET /jobs/{job_id} response"""
    job_id: str
    status: JobStatus
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: str
    updated_at: str
    error: Optional[str] = None


class SlideReportItem(BaseModel):
    """Single slide report item"""
    slide_id: str
    overflow_detected: bool = False
    actions: List[Dict[str, Any]] = Field(default_factory=list)


class JobReportResponse(BaseModel):
    """GET /jobs/{job_id}/report response"""
    job_id: str
    slides: List[SlideReportItem] = Field(default_factory=list)
    total_slides: int = 0
    generation_time: Optional[float] = None
    render_time: Optional[float] = None


class JobData(BaseModel):
    """Internal job data model"""
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    
    # Request data
    prompt: str = ""
    template_id: str = "default"
    language: str = "auto"
    density: str = "normal"
    
    # Result data
    output_path: Optional[str] = None
    num_slides: int = 0
    generation_time: Optional[float] = None
    render_time: Optional[float] = None
    report: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True

