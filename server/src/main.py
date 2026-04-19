from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api import crawler, articles, upload, search, stats, skill, graph

app = FastAPI(title="FinanceIntel Hub API", version="0.1.0")

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


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
