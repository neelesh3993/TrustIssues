from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.middleware.logging import logging_middleware
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="Trust Issues API",
    description="Real-time content credibility analysis",
    version="1.0.0",
)

# Add CORS middleware to support Chrome extension requests from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Include analyze routes
app.include_router(analyze_router)


@app.on_event("startup")
def startup():
    print("Initializing database...")
    init_db()


@app.get("/")
def health_check():
    return {"status": "backend running"}


@app.get("/health")
def health_status():
    """Health check endpoint for extension"""
    return {"status": "ok", "backend": "ready"}
