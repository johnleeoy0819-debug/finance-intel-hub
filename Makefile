.PHONY: dev install test db-migrate db-upgrade db-reset build prod

# ── 开发 ─────────────────────────
dev:
	@echo "启动后端..."
	cd server && uvicorn src.main:app --reload --port 8000 &
	@echo "启动前端..."
	cd web && npm run dev

# ── 安装 ─────────────────────────
install:
	cd server && pip install -r requirements.txt
	cd web && npm install

# ── 数据库 ───────────────────────
db-migrate:
	cd server && alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd server && alembic upgrade head

db-reset:
	rm -f data/hub.db && cd server && alembic upgrade head

# ── 测试 ─────────────────────────
test:
	cd server && pytest tests/ -v

# ── 生产 ─────────────────────────
build:
	cd web && npm run build

prod:
	cd server && uvicorn src.main:app --host 0.0.0.0 --port 8000
