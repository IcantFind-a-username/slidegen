"""Schemas Package"""

from .slide_schema import (
    SlideType, ThemeColor, ContentPriority,
    BulletPointSchema, TableSchema, CodeBlockSchema,
    SlideContentSchema, PresentationMetadataSchema,
    SlidedeckSchema, GenerationResultSchema,
    validate_slide_json, create_example_slidedeck,
)

from .job_schema import (
    JobStatus, GenerateRequest, GenerateResponse,
    JobStatusResponse, JobReportResponse, SlideReportItem, JobData,
)

__all__ = [
    # Slide schemas
    'SlideType', 'ThemeColor', 'ContentPriority',
    'BulletPointSchema', 'TableSchema', 'CodeBlockSchema',
    'SlideContentSchema', 'PresentationMetadataSchema',
    'SlidedeckSchema', 'GenerationResultSchema',
    'validate_slide_json', 'create_example_slidedeck',
    # Job schemas
    'JobStatus', 'GenerateRequest', 'GenerateResponse',
    'JobStatusResponse', 'JobReportResponse', 'SlideReportItem', 'JobData',
]