"""
Job Store - In-memory job storage with optional file persistence
"""

import json
import os
import threading
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path

from ..schemas.job_schema import JobData, JobStatus


class JobStore:
    """Thread-safe in-memory job store with file persistence"""
    
    def __init__(self, data_dir: str = "data"):
        self._jobs: Dict[str, JobData] = {}
        self._lock = threading.RLock()
        self._data_dir = Path(data_dir)
        self._jobs_file = self._data_dir / "jobs.json"
        
        # Ensure data directory exists
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing jobs from file (optional, for persistence across restarts)
        self._load_jobs()
    
    def _load_jobs(self):
        """Load jobs from file if exists"""
        try:
            if self._jobs_file.exists():
                with open(self._jobs_file, 'r') as f:
                    data = json.load(f)
                    for job_id, job_dict in data.items():
                        # Convert string dates back to datetime
                        job_dict['created_at'] = datetime.fromisoformat(job_dict['created_at'])
                        job_dict['updated_at'] = datetime.fromisoformat(job_dict['updated_at'])
                        self._jobs[job_id] = JobData(**job_dict)
        except Exception as e:
            print(f"Warning: Could not load jobs from file: {e}")
    
    def _save_jobs(self):
        """Save jobs to file"""
        try:
            data = {}
            for job_id, job in self._jobs.items():
                job_dict = job.model_dump()
                # Convert datetime to ISO string
                job_dict['created_at'] = job.created_at.isoformat()
                job_dict['updated_at'] = job.updated_at.isoformat()
                data[job_id] = job_dict
            
            with open(self._jobs_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save jobs to file: {e}")
    
    def create_job(self, job_id: str, prompt: str, template_id: str = "default",
                   language: str = "auto", density: str = "normal") -> JobData:
        """Create a new job"""
        with self._lock:
            now = datetime.utcnow()
            job = JobData(
                job_id=job_id,
                status=JobStatus.QUEUED,
                progress=0.0,
                created_at=now,
                updated_at=now,
                prompt=prompt,
                template_id=template_id,
                language=language,
                density=density
            )
            self._jobs[job_id] = job
            self._save_jobs()
            return job
    
    def get_job(self, job_id: str) -> Optional[JobData]:
        """Get job by ID"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs) -> Optional[JobData]:
        """Update job fields"""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            job.updated_at = datetime.utcnow()
            self._save_jobs()
            return job
    
    def set_status(self, job_id: str, status: JobStatus, progress: float = None,
                   error: str = None) -> Optional[JobData]:
        """Update job status"""
        updates = {'status': status}
        if progress is not None:
            updates['progress'] = progress
        if error is not None:
            updates['error'] = error
        return self.update_job(job_id, **updates)
    
    def set_result(self, job_id: str, output_path: str, num_slides: int,
                   generation_time: float = None, render_time: float = None,
                   report: dict = None) -> Optional[JobData]:
        """Set job result"""
        return self.update_job(
            job_id,
            status=JobStatus.DONE,
            progress=1.0,
            output_path=output_path,
            num_slides=num_slides,
            generation_time=generation_time,
            render_time=render_time,
            report=report
        )
    
    def set_failed(self, job_id: str, error: str) -> Optional[JobData]:
        """Mark job as failed"""
        return self.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=error
        )
    
    def list_jobs(self) -> Dict[str, JobData]:
        """List all jobs"""
        with self._lock:
            return dict(self._jobs)
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                self._save_jobs()
                return True
            return False


# Global job store instance
job_store = JobStore()

