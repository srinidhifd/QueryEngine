"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from utils import logger
from api import routes, middleware as api_middleware

# Initialize logger
app_logger = logger.setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    app_logger.info("application_startup", extra={"version": "1.0.0"})
    try:
        from services.database import init_db
        from services.seed_data import seed_database
        init_db()
        app_logger.info("database_initialized")
        seed_database()
        app_logger.info("database_seeding_complete")
    except Exception as e:
        app_logger.error("database_init_failed", extra={"error": str(e)})
        raise
    yield
    app_logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="NLP-to-SQL API",
    description="Natural Language to SQL + pytest Generation API",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
api_middleware.setup(app)

# Include routers
app.include_router(routes.router, prefix="/api")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nlp-to-sql-api",
        "version": "1.0.0"
    }


@app.get("/ready")
async def ready():
    """Readiness check endpoint (checks dependencies)."""
    return {
        "status": "ready",
        "api_key_configured": bool(settings.ANTHROPIC_API_KEY),
        "model": settings.MODEL
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NLP-to-SQL API",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_config=None  # Use custom logging
    )
