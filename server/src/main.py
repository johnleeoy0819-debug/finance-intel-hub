from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api import crawler, articles, upload, search, stats, skill, graph, publications, categories, wiki, lint, operations, export
from src.api import settings as user_settings
from src.core.scheduler import start_scheduler, shutdown_scheduler
from src.db.seed import seed_categories
from src.db.engine import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage APScheduler lifecycle with the app."""
    # Seed default data on startup
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Johnlee's KnowledgeBase API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawler.router, prefix="/api/crawler", tags=["crawler"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(skill.router, prefix="/api/skill", tags=["skill"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(publications.router, prefix="/api/publications", tags=["publications"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(wiki.router, prefix="/api/wiki", tags=["wiki"])
app.include_router(lint.router, prefix="/api/lint", tags=["lint"])
app.include_router(user_settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(operations.router, prefix="/api/operations", tags=["operations"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
