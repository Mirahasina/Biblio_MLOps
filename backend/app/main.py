from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, check_db_connection, engine, wait_for_db
from app.models import Book  # noqa: F401
from app.routes import books


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Bibliothèque API",
    description="CRUD API for books management (PostgreSQL)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)


@app.get("/health")
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "books-api",
        "database": "postgresql",
        "db_connected": db_ok,
    }
