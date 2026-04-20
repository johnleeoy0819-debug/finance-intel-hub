from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


def _find_project_root() -> Path:
    """从当前文件向上查找项目根目录（包含README.md的目录）"""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "README.md").exists() or (parent / ".env.example").exists():
            return parent
    # fallback: 当前文件的祖父的祖父（server/src/config.py -> server/ -> project/）
    return current.parent.parent


PROJECT_ROOT = _find_project_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"))

    # AI — LLM calls (chat, summary, classify, etc.)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL_PRIMARY: str = "gpt-4o"
    OPENAI_MODEL_FAST: str = "gpt-4o-mini"
    
    # LLM Provider: "openai" | "moonshot"
    LLM_PROVIDER: str = "openai"
    
    # Whisper (audio/video transcription) — requires real OpenAI API
    WHISPER_API_KEY: str = ""
    WHISPER_BASE_URL: str = "https://api.openai.com/v1"
    
    # Crawler
    FIRECRAWL_API_KEY: str = ""
    
    # Storage
    DATA_DIR: str = str(PROJECT_ROOT / "data")
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'hub.db'}"
    VECTOR_DB: str = "chroma"
    VECTOR_DB_PATH: str = str(PROJECT_ROOT / "data" / "chroma")
    STORAGE_BACKEND: str = "local"
    STORAGE_PATH: str = str(PROJECT_ROOT / "data")
    
    # Server
    SERVER_PORT: int = Field(default=8000, ge=1, le=65535)
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # Skill
    SKILL_FEEDBACK_ENABLED: bool = True
    SKILL_EVOLUTION_ENABLED: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
