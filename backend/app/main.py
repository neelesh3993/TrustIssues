from fastapi import FastAPI
from app.database.db import init_db
from app.middleware.logging import logging_middleware

app = FastAPI()

app.middleware("http")(logging_middleware)


@app.on_event("startup")
def startup():
    print("Initializing database...")
    init_db()


@app.get("/")
def health_check():
    return {"status": "backend running"}
