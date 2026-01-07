"""
API Routes for PPT Generation

Endpoints:
- POST /generate         - Create a generation job
- GET /jobs/{job_id}     - Get job status
- GET /jobs/{job_id}/download - Download generated PPTX
- GET /jobs/{job_id}/report   - Get render report
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from ..schemas.job_schema import (
    GenerateRequest, GenerateResponse,
    JobStatusResponse, JobReportResponse, SlideReportItem,
    JobStatus
)
from ..core.job_store import job_store
from ..services.run_pipeline import run_generation_pipeline


router = APIRouter()


def generate_job_id() -> str:
    """Generate a unique job ID"""
    return f"job_{uuid.uuid4().hex[:12]}"


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def create_generation_job(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new PPT generation job.
    
    The job runs asynchronously in the background.
    Poll GET /jobs/{job_id} to check status.
    """
    # Generate unique job ID
    job_id = generate_job_id()
    
    # Create job in store
    job_store.create_job(
        job_id=job_id,
        prompt=request.prompt,
        template_id=request.template_id,
        language=request.language,
        density=request.density
    )
    
    # Run pipeline in background
    background_tasks.add_task(
        run_generation_pipeline,
        job_id=job_id,
        prompt=request.prompt,
        language=request.language,
        density=request.density,
        template_id=request.template_id
    )
    
    return GenerateResponse(
        job_id=job_id,
        status=JobStatus.QUEUED
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a generation job.
    
    Status values:
    - queued: Job is waiting to start
    - generating_json: LLM is generating slide content
    - rendering: PPTX file is being created
    - done: Generation complete, ready for download
    - failed: Generation failed (check error field)
    """
    job = job_store.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        error=job.error
    )


@router.get("/jobs/{job_id}/download")
async def download_pptx(job_id: str):
    """
    Download the generated PPTX file.
    
    Only available when job status is 'done'.
    Returns 409 Conflict if job is not complete.
    Returns 404 if file not found.
    """
    job = job_store.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(
            status_code=409, 
            detail=f"Job not done. Current status: {job.status}"
        )
    
    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file path not set")
    
    file_path = Path(job.output_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=str(file_path),
        filename=f"presentation_{job_id}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@router.get("/jobs/{job_id}/report", response_model=JobReportResponse)
async def get_job_report(job_id: str):
    """
    Get the render report for a completed job.
    
    The report includes:
    - Slide-by-slide information
    - Overflow detection results
    - Any automatic adjustments made
    """
    job = job_store.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(
            status_code=409,
            detail=f"Report only available for completed jobs. Current status: {job.status}"
        )
    
    # Build report from stored data
    report_data = job.report or {}
    slides = []
    
    for slide_info in report_data.get('slides', []):
        slides.append(SlideReportItem(
            slide_id=slide_info.get('slide_id', 'unknown'),
            overflow_detected=slide_info.get('overflow_detected', False),
            actions=slide_info.get('actions', [])
        ))
    
    return JobReportResponse(
        job_id=job_id,
        slides=slides,
        total_slides=report_data.get('total_slides', len(slides)),
        generation_time=report_data.get('generation_time'),
        render_time=report_data.get('render_time')
    )

