"""
SlideGen Backend - FastAPI Application Entry Point

Run with:
    uvicorn app.main:app --reload --port 8000

Or:
    python -m uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.generate import router as generate_router

# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="SlideGen API",
    description="AI-powered PowerPoint generation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# CORS MIDDLEWARE
# Allow frontend on localhost:8080 to access the API
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # In case you use a different port
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROUTES
# ============================================================

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "slidegen-api"}


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "service": "SlideGen API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz"
    }


# Include generation routes
app.include_router(generate_router, tags=["Generation"])


# ============================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print("=" * 50)
    print("SlideGen API Starting...")
    print("=" * 50)
    print("  Docs:    http://localhost:8000/docs")
    print("  Health:  http://localhost:8000/healthz")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print("SlideGen API Shutting down...")

