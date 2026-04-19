# FinanceIntel Hub MVP Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:test-driven-development for every module, superpowers:verification-before-completion before claiming completion.

**Goal:** Build a minimal viable FinanceIntel Hub with web crawler, AI processing pipeline, SQLite storage, web frontend, and basic SKILL integration.

**Architecture:** FastAPI backend with SQLAlchemy + ChromaDB, React frontend with TailwindCSS, OpenAI API for AI processing, Firecrawl for web crawling.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, ChromaDB, OpenAI SDK, React 18, Vite, TailwindCSS, Zustand, pytest

---

## File Structure Overview

```
finance-intel-hub/
├── server/
│   ├── src/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/ (crawler, articles, upload, search, stats, skill)
│   │   ├── core/ (crawler, processor, uploader, search, scheduler, feedback, storage)
│   │   ├── db/ (engine, models, migrations/)
│   │   └── prompts/ (v1/*.yaml, loader.py)
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
├── web/
│   ├── src/
│   │   ├── main.tsx, App.tsx
│   │   ├── pages/ (Dashboard, Library, ArticleDetail, Sources, Upload)
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/client.ts
│   │   ├── store/
│   │   └── types/
│   ├── index.html
│   ├── package.json
│   └── tailwind.config.ts
├── data/
├── skills/econ-master/SKILL.md
├── .env.example
├── Makefile
└── README.md
```

---

## Chunk 1: Project Skeleton & Configuration

### Task 1.1: Root Configuration Files

**Files:**
- Create: `.env.example`
- Create: `.gitignore`
- Create: `Makefile`
- Create: `README.md` (minimal)

**TDD Steps:**
- [ ] **Step 1 (RED):** No tests needed for config files; verify file structure
- [ ] **Step 2:** Create `.env.example` with all required env vars from design spec
- [ ] **Step 3:** Create `Makefile` with `install`, `dev`, `db-migrate`, `db-upgrade`, `test` targets
- [ ] **Step 4:** Run `make install` (dry run check that commands are valid)
- [ ] **Step 5:** Verify all files exist with correct content

### Task 1.2: Backend Skeleton

**Files:**
- Create: `server/pyproject.toml`
- Create: `server/requirements.txt`
- Create: `server/alembic.ini`
- Create: `server/src/__init__.py`
- Create: `server/tests/__init__.py`
- Create: `server/src/db/migrations/env.py`
- Create: `server/src/db/migrations/versions/.gitkeep`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_import_structure` — asserts all key modules can be imported
- [ ] **Step 2:** Run `pytest server/tests/test_structure.py -v` → expect FAIL (files don't exist)
- [ ] **Step 3 (GREEN):** Create all skeleton files with minimal valid content
- [ ] **Step 4:** Run test → PASS

### Task 1.3: Frontend Skeleton

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/vite.config.ts`
- Create: `web/tailwind.config.ts`
- Create: `web/index.html`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/types/index.ts`

**TDD Steps:**
- [ ] **Step 1 (RED):** No unit tests; verify `npm install` succeeds and `npm run dev` starts without error
- [ ] **Step 2:** Create all config files
- [ ] **Step 3:** Run `cd web && npm install` → must succeed
- [ ] **Step 4:** Run `cd web && npx tsc --noEmit` → must pass (no type errors)

---

## Chunk 2: Database Layer

### Task 2.1: SQLAlchemy Engine & Session

**Files:**
- Create: `server/src/db/engine.py`
- Create: `server/src/config.py`
- Test: `server/tests/test_db_engine.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_engine_creates_sqlite_db` — asserts engine connects and creates file
- [ ] **Step 2:** Run `pytest server/tests/test_db_engine.py -v` → FAIL
- [ ] **Step 3 (GREEN):** Implement `config.py` with Pydantic Settings, `engine.py` with `create_engine`
- [ ] **Step 4:** Run test → PASS
- [ ] **Step 5 (REFACTOR):** Add sessionmaker, async support if needed

### Task 2.2: ORM Models

**Files:**
- Create: `server/src/db/models.py`
- Test: `server/tests/test_models.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests for all models: `test_article_model`, `test_category_model`, `test_tag_model`, `test_source_model`, `test_knowledge_edge_model`, `test_upload_task_model`, `test_skill_feedback_model`, `test_correction_model`
- [ ] **Step 2:** Run tests → FAIL (models don't exist)
- [ ] **Step 3 (GREEN):** Implement all SQLAlchemy models per design spec §8.2
- [ ] **Step 4:** Run tests → PASS (create instances, verify fields, verify relationships)

### Task 2.3: Alembic Initial Migration

**Files:**
- Create: `server/src/db/migrations/versions/001_initial.py`
- Test: `server/tests/test_migrations.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_migration_creates_all_tables` — runs upgrade, checks all tables exist
- [ ] **Step 2:** Run test → FAIL (no migration file)
- [ ] **Step 3 (GREEN):** Generate initial migration via `alembic revision --autogenerate`, review and commit
- [ ] **Step 4:** Run test → PASS

---

## Chunk 3: Prompt System

### Task 3.1: Prompt Loader

**Files:**
- Create: `server/src/prompts/loader.py`
- Create: `server/src/prompts/v1/cleaner.yaml`
- Test: `server/tests/test_prompt_loader.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_load_cleaner_prompt` — asserts returns dict with version/name/system/user keys
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `loader.py` that reads YAML, validates structure, renders Jinja2 templates
- [ ] **Step 4:** Run test → PASS

### Task 3.2: All Prompt YAML Files

**Files:**
- Create: `server/src/prompts/v1/summarizer.yaml`
- Create: `server/src/prompts/v1/classifier.yaml`
- Create: `server/src/prompts/v1/tagger.yaml`
- Create: `server/src/prompts/v1/mindmap.yaml`
- Create: `server/src/prompts/v1/relation.yaml`
- Create: `server/src/prompts/v1/video.yaml`
- Create: `server/src/prompts/v1/publication.yaml`
- Test: `server/tests/test_prompts.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_all_prompts_loadable` — iterates all YAML files, loads each, checks required fields
- [ ] **Step 2:** Run test → FAIL (files don't exist)
- [ ] **Step 3 (GREEN):** Create all 8 YAML prompt files per design spec §7
- [ ] **Step 4:** Run test → PASS
- [ ] **Step 5:** Write test `test_prompt_rendering` — loads classifier, renders with sample inputs, checks output contains expected text
- [ ] **Step 6:** Run test → PASS

---

## Chunk 4: AI Processing Core

### Task 4.1: OpenAI Client Wrapper

**Files:**
- Create: `server/src/core/ai_client.py`
- Test: `server/tests/test_ai_client.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_ai_client_loads_prompt_and_calls_api` — mocks OpenAI call, verifies prompt template is rendered and sent
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `ai_client.py` with `run_prompt(name, **kwargs)` function
- [ ] **Step 4:** Run test → PASS

### Task 4.2: Content Cleaner

**Files:**
- Modify: `server/src/core/processor.py`
- Test: `server/tests/test_processor_clean.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_clean_html_returns_text` — inputs raw HTML with ads, expects clean text or [IRRELEVANT]
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `clean_content(raw_html)` in processor.py using ai_client
- [ ] **Step 4:** Run test → PASS (with mocked AI response)

### Task 4.3: Article Pipeline (Summary + Category + Tags)

**Files:**
- Modify: `server/src/core/processor.py`
- Test: `server/tests/test_processor_pipeline.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests for `summarize()`, `classify()`, `extract_tags()` — each returns expected JSON structure
- [ ] **Step 2:** Run tests → FAIL
- [ ] **Step 3 (GREEN):** Implement three functions in processor.py
- [ ] **Step 4:** Run tests → PASS (with mocked AI)

### Task 4.4: Full Pipeline Integration

**Files:**
- Modify: `server/src/core/processor.py`
- Test: `server/tests/test_processor_integration.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_process_article_end_to_end` — inputs raw HTML, expects article dict with all fields populated
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `process_article(raw_html, source_url)` orchestrator with status tracking
- [ ] **Step 4:** Run test → PASS

---

## Chunk 5: Crawler Engine

### Task 5.1: Firecrawl Driver

**Files:**
- Create: `server/src/core/crawler.py`
- Test: `server/tests/test_crawler_firecrawl.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_firecrawl_driver_returns_markdown` — mocks Firecrawl API, expects list of articles with markdown content
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `FirecrawlDriver` class with `crawl(source_config)` method
- [ ] **Step 4:** Run test → PASS

### Task 5.2: Duplicate Detection

**Files:**
- Modify: `server/src/core/crawler.py`
- Test: `server/tests/test_crawler_dedup.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_is_duplicate_detects_same_url` — inserts article, checks duplicate detection
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `is_duplicate(url)` using URL exact match + title similarity
- [ ] **Step 4:** Run test → PASS

### Task 5.3: Scheduler Integration

**Files:**
- Create: `server/src/core/scheduler.py`
- Test: `server/tests/test_scheduler.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_scheduler_triggers_crawl` — verifies APScheduler job is registered and fires
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement scheduler with `add_source()`, `remove_source()`, `trigger_now()`
- [ ] **Step 4:** Run test → PASS

---

## Chunk 6: Storage & Upload

### Task 6.1: Storage Backend (Abstract + Local)

**Files:**
- Create: `server/src/core/storage.py`
- Test: `server/tests/test_storage.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests `test_local_storage_save_load_delete` — saves bytes, loads back, deletes
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `StorageBackend` ABC and `LocalStorage`
- [ ] **Step 4:** Run test → PASS

### Task 6.2: File Uploader

**Files:**
- Create: `server/src/core/uploader.py`
- Test: `server/tests/test_uploader.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests for PDF/Word/TXT parsing — inputs sample files, expects text extraction
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `process_upload(file_path, file_type)` with format-specific parsers
- [ ] **Step 4:** Run test → PASS (use test fixtures in tests/fixtures/)

---

## Chunk 7: API Layer

### Task 7.1: FastAPI App & Routers

**Files:**
- Create: `server/src/main.py`
- Create: `server/src/api/__init__.py`
- Create: `server/src/api/crawler.py`
- Create: `server/src/api/articles.py`
- Create: `server/src/api/upload.py`
- Create: `server/src/api/search.py`
- Create: `server/src/api/stats.py`
- Create: `server/src/api/skill.py`
- Test: `server/tests/test_api.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_api_routes_exist` — uses TestClient to hit each endpoint, verifies 200/422 (not 404)
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement all routers with request/response Pydantic models
- [ ] **Step 4:** Run test → PASS

### Task 7.2: Article CRUD Endpoints

**Files:**
- Modify: `server/src/api/articles.py`
- Test: `server/tests/test_api_articles.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests for GET /api/articles, GET /api/articles/{id}, DELETE /api/articles/{id}
- [ ] **Step 2:** Run tests → FAIL
- [ ] **Step 3 (GREEN):** Implement CRUD operations using SQLAlchemy
- [ ] **Step 4:** Run tests → PASS

### Task 7.3: Search Endpoints

**Files:**
- Create: `server/src/core/search.py`
- Modify: `server/src/api/search.py`
- Test: `server/tests/test_search.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_fulltext_search_returns_results` — inserts articles, searches keyword, verifies results
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement FTS5 search in search.py, wire to API
- [ ] **Step 4:** Run test → PASS

---

## Chunk 8: Frontend Core

### Task 8.1: API Client

**Files:**
- Create: `web/src/api/client.ts`
- Test: `web/src/api/client.test.ts` (optional, or manual verification)

**TDD Steps:**
- [ ] **Step 1:** Create typed API client with axios/fetch wrapper for all backend endpoints
- [ ] **Step 2:** Verify TypeScript compiles with `npx tsc --noEmit`

### Task 8.2: Zustand Store

**Files:**
- Create: `web/src/store/index.ts`
- Test: Manual verification

**TDD Steps:**
- [ ] **Step 1:** Implement store slices: articles, search, upload, sources
- [ ] **Step 2:** Verify store works in a simple React component test

### Task 8.3: Shared Components

**Files:**
- Create: `web/src/components/ArticleCard.tsx`
- Create: `web/src/components/TagList.tsx`
- Create: `web/src/components/CategoryTree.tsx`
- Create: `web/src/components/SearchBar.tsx`
- Create: `web/src/components/FileUploader.tsx`

**TDD Steps:**
- [ ] **Step 1:** Implement each component with props interfaces
- [ ] **Step 2:** Verify with `npx tsc --noEmit`

---

## Chunk 9: Frontend Pages

### Task 9.1: Dashboard Page

**Files:**
- Create: `web/src/pages/Dashboard.tsx`
- Test: Manual browser verification

**Steps:**
- [ ] **Step 1:** Implement dashboard with stat cards, charts placeholder, recent articles list
- [ ] **Step 2:** Wire to API client for real data
- [ ] **Step 3:** Verify responsive layout on mobile/desktop

### Task 9.2: Library Page

**Files:**
- Create: `web/src/pages/Library.tsx`

**Steps:**
- [ ] **Step 1:** Implement two-column layout (category tree + article list)
- [ ] **Step 2:** Implement category filtering and tag filtering
- [ ] **Step 3:** Wire search API

### Task 9.3: Article Detail Page

**Files:**
- Create: `web/src/pages/ArticleDetail.tsx`

**Steps:**
- [ ] **Step 1:** Implement tab navigation (原文/AI摘要/思维导图/关联文章)
- [ ] **Step 2:** Integrate markmap for mindmap rendering
- [ ] **Step 3:** Add 👍👎 feedback buttons

### Task 9.4: Sources & Upload Pages

**Files:**
- Create: `web/src/pages/Sources.tsx`
- Create: `web/src/pages/Upload.tsx`

**Steps:**
- [ ] **Step 1:** Sources page with CRUD for crawler sources
- [ ] **Step 2:** Upload page with drag-drop and progress tracking

---

## Chunk 10: SKILL Integration

### Task 10.1: SKILL.md File

**Files:**
- Create: `skills/econ-master/SKILL.md`

**Steps:**
- [ ] **Step 1:** Write complete SKILL.md per design spec §13.1
- [ ] **Step 2:** Verify markdown structure is valid

### Task 10.2: SKILL API Endpoints

**Files:**
- Modify: `server/src/api/skill.py`
- Test: `server/tests/test_skill_api.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write tests for POST /api/skill/feedback, GET /api/skill/memory
- [ ] **Step 2:** Run tests → FAIL
- [ ] **Step 3 (GREEN):** Implement endpoints with database writes
- [ ] **Step 4:** Run tests → PASS

### Task 10.3: Few-shot Sample Builder (P1 level, MVP basic)

**Files:**
- Modify: `server/src/core/feedback.py`
- Test: `server/tests/test_feedback.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_build_fewshot_from_corrections` — inserts corrections, expects few-shot JSON
- [ ] **Step 2:** Run test → FAIL
- [ ] **Step 3 (GREEN):** Implement `build_fewshot_samples()` that aggregates corrections by field
- [ ] **Step 4:** Run test → PASS

---

## Chunk 11: Integration & End-to-End

### Task 11.1: Full Pipeline Test

**Files:**
- Test: `server/tests/test_e2e_pipeline.py`

**TDD Steps:**
- [ ] **Step 1 (RED):** Write test `test_e2e_crawl_process_store` — triggers crawl, processes article, verifies DB + Markdown + FTS index
- [ ] **Step 2:** Run test → likely FAIL on first run
- [ ] **Step 3:** Fix any integration issues
- [ ] **Step 4:** Run test → PASS

### Task 11.2: Frontend-Backend Integration

**Steps:**
- [ ] **Step 1:** Start backend (`make dev` backend only)
- [ ] **Step 2:** Verify all API endpoints with curl/Postman
- [ ] **Step 3:** Start frontend, verify pages load and data flows correctly

### Task 11.3: Verification Checklist

Before claiming MVP complete:
- [ ] All backend tests pass: `cd server && pytest tests/ -v`
- [ ] Frontend compiles: `cd web && npx tsc --noEmit`
- [ ] Backend starts without error: `cd server && uvicorn src.main:app --reload`
- [ ] Frontend starts without error: `cd web && npm run dev`
- [ ] API docs accessible: `http://localhost:8000/docs`
- [ ] Can add a crawler source via API/UI
- [ ] Can trigger manual crawl
- [ ] Article appears in DB and frontend
- [ ] Search returns results
- [ ] Upload works for PDF/Word
- [ ] SKILL.md is complete and loadable

---

*Plan complete. Each chunk is logically self-contained. Execute in order, strict TDD per task.*
