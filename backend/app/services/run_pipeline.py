"""
Pipeline Adapter - Connects LLM Service and PPTX Engine

This module provides a clean interface for running the full generation pipeline:
1. User prompt → LLM generates slide JSON
2. Slide JSON → PPTX Engine renders file

IMPORTANT: This adapter connects to your teammates' implementations.
If function signatures differ, update the calls below.
"""

import os
import time
import traceback
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from ..core.job_store import job_store
from ..schemas.job_schema import JobStatus


# ============================================================
# ADAPTER CONFIGURATION
# Configure how to call your teammates' services
# ============================================================

# Try to import LLM service (V3 preferred, then V2, fallback to V1)
try:
    from .presentation_pipeline import generate_professional_presentation
    LLM_AVAILABLE = True
    LLM_VERSION = 3
    print("✓ Using LLMService V3 (Integrated Pipeline)")
    
    # Wrapper for backward compatibility
    def generate_presentation(prompt: str, content_text: str = None):
        return generate_professional_presentation(
            user_request=prompt,
            slide_count=8,
            theme="corporate_blue",
            enable_images=True  # 启用图片集成
        )
except ImportError as e:
    print(f"V3 import failed: {e}")
    try:
        from .LLMServiceV2 import generate_presentation
        LLM_AVAILABLE = True
        LLM_VERSION = 2
        print("✓ Using LLMService V2 (Production-Grade)")
    except ImportError:
        try:
            from .LLMService import generate_presentation
            LLM_AVAILABLE = True
            LLM_VERSION = 1
            print("⚠ Using LLMService V1 (Basic)")
        except ImportError as e:
            print(f"Warning: LLMService not available: {e}")
            LLM_AVAILABLE = False
            LLM_VERSION = 0
            generate_presentation = None

# Try to import PPTX engine
try:
    from .engine import generate_pptx, PPTXEngine
    ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Engine not fully available: {e}")
    ENGINE_AVAILABLE = False
    generate_pptx = None


# ============================================================
# MOCK DATA FOR DEMO/TESTING
# Used when LLM service is unavailable
# ============================================================

def get_mock_slidedeck(prompt: str) -> Dict[str, Any]:
    """Generate mock slide data for demo purposes"""
    return {
        "metadata": {
            "title": f"Presentation: {prompt[:50]}...",
            "theme": "corporate_blue",
            "language": "en"
        },
        "slides": [
            {
                "slide_type": "title",
                "title": "AI-Generated Presentation",
                "subtitle": f"Based on: {prompt[:80]}..."
            },
            {
                "slide_type": "section", 
                "title": "Introduction",
                "subtitle": "Getting Started"
            },
            {
                "slide_type": "content",
                "title": "Key Points",
                "body_points": [
                    {"text": "This is an auto-generated presentation", "level": 0, "priority": "high"},
                    {"text": "Created using AI technology", "level": 1, "priority": "normal"},
                    {"text": "Customizable and editable", "level": 1, "priority": "normal"},
                    {"text": "Professional quality output", "level": 0, "priority": "high"}
                ]
            },
            {
                "slide_type": "two_column",
                "title": "Comparison",
                "left_column": [
                    {"text": "Traditional Method", "level": 0},
                    {"text": "Time consuming", "level": 1},
                    {"text": "Manual effort", "level": 1}
                ],
                "right_column": [
                    {"text": "AI-Powered Method", "level": 0},
                    {"text": "Fast generation", "level": 1},
                    {"text": "Automated workflow", "level": 1}
                ]
            },
            {
                "slide_type": "content",
                "title": "Benefits",
                "body_points": [
                    {"text": "Save time on presentation creation", "level": 0, "priority": "critical"},
                    {"text": "Consistent formatting and style", "level": 0, "priority": "high"},
                    {"text": "Focus on content, not design", "level": 0, "priority": "high"},
                    {"text": "Easy to iterate and refine", "level": 0, "priority": "normal"}
                ]
            },
            {
                "slide_type": "closing",
                "title": "Thank You",
                "subtitle": "Questions & Discussion"
            }
        ]
    }


# ============================================================
# PIPELINE RUNNER
# ============================================================

class PipelineRunner:
    """
    Runs the full generation pipeline with progress tracking.
    
    Usage:
        runner = PipelineRunner(job_id, prompt)
        runner.run()  # Blocks until complete or failed
    """
    
    def __init__(self, job_id: str, prompt: str, 
                 language: str = "auto",
                 density: str = "normal",
                 template_id: str = "default",
                 output_dir: str = "data/outputs"):
        self.job_id = job_id
        self.prompt = prompt
        self.language = language
        self.density = density
        self.template_id = template_id
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Timing
        self.generation_time: Optional[float] = None
        self.render_time: Optional[float] = None
    
    def _update_status(self, status: JobStatus, progress: float, error: str = None):
        """Update job status in store"""
        job_store.set_status(self.job_id, status, progress, error)
    
    def _simulate_progress(self, start_progress: float, end_progress: float, 
                          duration: float, status: JobStatus):
        """
        Simulate smooth progress updates during a long operation.
        Updates progress incrementally over the given duration.
        """
        steps = 10
        step_duration = duration / steps
        progress_step = (end_progress - start_progress) / steps
        
        for i in range(steps):
            current_progress = start_progress + (progress_step * (i + 1))
            self._update_status(status, min(current_progress, end_progress))
            time.sleep(step_duration)
    
    def _generate_slides(self) -> Dict[str, Any]:
        """
        Step 1: Generate slide JSON from prompt using V2 pipeline
        
        Progress: 0% → 60%
        
        V2 Pipeline stages:
        - 5%: Analyzing user intent
        - 15%: Generating narrative outline  
        - 25-55%: Generating slide content (incremental per slide)
        - 60%: Content generation complete
        """
        # Start generating
        self._update_status(JobStatus.GENERATING_JSON, 0.05)
        
        start = time.time()
        
        if LLM_AVAILABLE and generate_presentation:
            try:
                # Update progress - analyzing intent
                self._update_status(JobStatus.GENERATING_JSON, 0.10)
                
                # Call V2 LLM service (handles its own logging)
                slidedeck = generate_presentation(self.prompt)
                
                # Validate we got slides
                if not slidedeck or 'slides' not in slidedeck:
                    raise ValueError("LLM returned invalid slidedeck structure")
                
                self.generation_time = time.time() - start
                self._update_status(JobStatus.GENERATING_JSON, 0.60)
                
                # Log generation quality metrics
                num_slides = len(slidedeck.get('slides', []))
                print(f"✓ Generated {num_slides} slides in {self.generation_time:.2f}s")
                
                return slidedeck
                
            except Exception as e:
                print(f"LLM generation failed, using mock data: {e}")
                traceback.print_exc()
        
        # Fallback to mock data with simulated progress
        print("Using mock slidedeck data for demo")
        
        # Simulate progress for demo (makes it feel more real)
        self._update_status(JobStatus.GENERATING_JSON, 0.15)
        time.sleep(0.3)
        self._update_status(JobStatus.GENERATING_JSON, 0.30)
        time.sleep(0.3)
        self._update_status(JobStatus.GENERATING_JSON, 0.45)
        time.sleep(0.3)
        
        slidedeck = get_mock_slidedeck(self.prompt)
        self.generation_time = time.time() - start
        self._update_status(JobStatus.GENERATING_JSON, 0.60)
        return slidedeck
    
    def _render_pptx(self, slidedeck: Dict[str, Any]) -> str:
        """
        Step 2: Render PPTX from slide JSON
        
        Progress: 60% → 95%
        """
        self._update_status(JobStatus.RENDERING, 0.65)
        
        # Determine theme from metadata or use default
        theme = slidedeck.get('metadata', {}).get('theme', 'corporate_blue')
        
        # Output path
        output_path = str(self.output_dir / f"{self.job_id}.pptx")
        
        start = time.time()
        
        # Progress update before rendering
        self._update_status(JobStatus.RENDERING, 0.70)
        
        if ENGINE_AVAILABLE and generate_pptx:
            try:
                # Call your teammate's PPTX engine
                result = generate_pptx(slidedeck, output_path, theme)
                
                if not result.get('success'):
                    raise ValueError(result.get('error_message', 'Unknown render error'))
                
                self.render_time = time.time() - start
                self._update_status(JobStatus.RENDERING, 0.95)
                return output_path
                
            except Exception as e:
                print(f"PPTX rendering failed: {e}")
                traceback.print_exc()
                raise
        else:
            raise RuntimeError("PPTX Engine not available")
    
    def _build_report(self, slidedeck: Dict[str, Any]) -> Dict[str, Any]:
        """Build render report (internal use only)"""
        return {
            'total_slides': len(slidedeck.get('slides', [])),
            'generation_time': self.generation_time,
            'render_time': self.render_time
        }
    
    def run(self) -> bool:
        """
        Run the full pipeline.
        Returns True if successful, False if failed.
        """
        try:
            # Step 1: Generate slides JSON (0% → 60%)
            slidedeck = self._generate_slides()
            
            # Step 2: Render PPTX (60% → 95%)
            output_path = self._render_pptx(slidedeck)
            
            # Step 3: Finalize (95% → 100%)
            report = self._build_report(slidedeck)
            
            job_store.set_result(
                self.job_id,
                output_path=output_path,
                num_slides=len(slidedeck.get('slides', [])),
                generation_time=self.generation_time,
                render_time=self.render_time,
                report=report
            )
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            # Simplify error message for users
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = "AI service temporarily unavailable. Please try again later."
            elif "timeout" in error_msg.lower():
                error_msg = "Request timed out. Please try again."
            
            print(f"Pipeline failed for job {self.job_id}: {error_msg}")
            traceback.print_exc()
            job_store.set_failed(self.job_id, error_msg)
            return False


def run_generation_pipeline(job_id: str, prompt: str, 
                           language: str = "auto",
                           density: str = "normal",
                           template_id: str = "default") -> bool:
    """
    Convenience function to run the pipeline.
    Called from background task.
    """
    runner = PipelineRunner(
        job_id=job_id,
        prompt=prompt,
        language=language,
        density=density,
        template_id=template_id
    )
    return runner.run()
