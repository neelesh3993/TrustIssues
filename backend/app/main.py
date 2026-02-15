from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database.db import init_db
from app.middleware.logging import logging_middleware
from app.routes.analyze import router as analyze_router
from app.core.settings import validate_required_keys

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trust Issues API",
    description="Real-time content credibility analysis",
    version="1.0.0",
)

# Add CORS middleware to support Chrome extension requests
# Allow all origins during development for easier testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including chrome-extension://)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Include analyze routes
app.include_router(analyze_router)


@app.on_event("startup")
def startup():
    """Initialize database and validate configuration."""
    print("Initializing TrustIssues backend...")
    
    # Validate required API keys
    try:
        validate_required_keys()
        print("✓ API keys configured correctly")
    except ValueError as e:
        print(f"⚠ Configuration warning: {str(e)}")
        # Don't fail startup, but print warning
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Backend ready!")
@app.get("/")
def health_check():
    return {"status": "backend running"}


@app.get("/health")
def health_status():
    """Health check endpoint for extension"""
    return {"status": "ok", "backend": "ready"}
