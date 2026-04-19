# FinanceIntel Hub

个人财经智识库系统 —— 自动采集、AI 整理、结构化存储、智能问答。

## 快速启动

```bash
# 1. 安装依赖
make install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 和 FIRECRAWL_API_KEY

# 3. 初始化数据库
make db-upgrade

# 4. 启动开发服务器
make dev

# 5. 打开浏览器访问 http://localhost:5173
```

## 技术栈

- **后端**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, ChromaDB
- **前端**: React 18, TypeScript, Vite, TailwindCSS, Zustand
- **AI**: OpenAI API (GPT-4o / gpt-4o-mini)
- **采集**: Firecrawl API

## 项目结构

```
finance-intel-hub/
├── server/          # FastAPI 后端
├── web/             # React 前端
├── data/            # 运行时数据（SQLite, Markdown, 向量库）
└── skills/          # AI SKILL 定义
```

## 文档

- [设计文档](docs/superpowers/specs/2026-04-20-finance-knowledge-hub-design_final.md)
- [实施计划](docs/superpowers/plans/2026-04-20-finance-intel-hub-mvp.md)
