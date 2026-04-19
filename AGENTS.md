# AGENTS.md — Johnlee's KnowledgeBase 项目记忆

> 本文件记录项目背景、技术决策、已知问题、用户偏好和开发教训。
> 每次修改代码前必读，避免重复犯错。

---

## 1. 项目基本信息

| 项 | 内容 |
|---|---|
| 项目名称 | Johnlee's KnowledgeBase |
| 仓库 | github.com/johnleeoy0819-debug/finance-intel-hub |
| 当前版本 | v1.0.1 + V1 Bug 修复（commit a0edbb6） |
| 工作目录 | /Users/lily/知识库建立 |
| 用户 | johnleeoy0819-debug |

### 技术栈
- **后端**：FastAPI + SQLAlchemy 2.0 + Alembic + SQLite + ChromaDB + OpenAI SDK
- **前端**：React 18 + Vite + TailwindCSS + Zustand + TypeScript
- **采集**：Playwright → Jina Reader → Firecrawl（三级 fallback）
- **向量搜索**：sentence-transformers/all-MiniLM-L6-v2
- **语音转录**：OpenAI Whisper-1
- **测试**：pytest（95 个测试全部通过）

### 已实现功能
- ✅ 三级 fallback 爬虫
- ✅ 语义搜索（ChromaDB）
- ✅ 知识图谱（D3.js）
- ✅ 视频处理（Whisper 转录）
- ✅ 文献管理（arXiv/CrossRef DOI）
- ✅ SKILL 进化闭环（👍👎 → Few-shot）
- ✅ Dashboard 仪表盘（Recharts）
- ✅ AI 问答对话页面（经济大师 RAG）
- ✅ URL 链接采集（文章+视频，yt-dlp）
- ✅ 默认分类 seed（7 大领域 35 子分类）
- ✅ V1 Bug 修复（14 个 P0/P1/P2 bug）

### 待实现功能（暂不实现 OCR）
- 🟡 PWA 支持
- 🟡 批量导入
- 🟡 Prompt A/B 测试
- 🟡 用户记忆精细化
- 🟡 推送通知
- 🔵 云端迁移（PostgreSQL/S3）
- 🔵 Capacitor App
- 🔵 多用户/多领域

---

## 2. 用户风格与偏好

**必须遵守的原则**：
1. **实用性优先** — "能跑起来"比"代码好看"重要得多
2. **直接指出问题** — 用户会直接说"前端页面显示 not found"，不会绕弯子
3. **主动验收** — 用户会要求按文档验收（V1 BUG.md、V1 REPAIR验收方案.md）
4. **快速迭代** — 用户喜欢"先做出来看效果"，不追求完美架构
5. **GitHub 同步** — 每次修复后必须推送到 GitHub
6. **测试驱动** — 修一个问题必须补对应测试，不引入回归

**用户习惯**：
- 会粘贴链接测试功能（URL 采集功能就是这样提出的）
- 会关注"AI 进化"相关的功能（SKILL 反馈、记忆、个性化）
- 对财经领域有深度需求（财报、政策、行业分析）

---

## 3. 我犯过的错误（教训清单）

### 错误 1：Python 3.9 类型注解不兼容
**表现**：在 `search.py` 中使用 `dict[int, float] | None`，运行时 `TypeError: unsupported operand type(s) for |`。
**原因**：Python 3.9 不支持 `|` 联合类型操作符（3.10+ 才支持）。
**修复**：改用 `Optional[Dict[int, float]]` 和 `List[Article]`。
**教训**：本项目运行环境是 **Python 3.9.6**，永远不能用 `list[T]`、`dict[K,V]`、`T | None` 语法。必须用 `typing` 模块的 `List`、`Dict`、`Optional`。

### 错误 2：类型定义循环冲突
**表现**：`client.ts` 同时从 `types` 导入 `DashboardStats` 又本地导出同名接口，导致 TypeScript 编译失败。
**原因**：类型定义分散在多处，没有统一来源。
**修复**：所有领域类型统一在 `types/index.ts` 定义，`client.ts` 只导入不重复定义。
**教训**：类型定义必须单一来源。API 层从 types 导入，不反向定义。

### 错误 3：未检查数据库状态就修复
**表现**：修复了分类映射 bug 后，categories 表仍然为空，AI 分类依然失败，前端分类树依然为空。
**原因**：只修了代码逻辑，没考虑"数据从哪里来"。
**修复**：新增 `seed.py`，在应用启动时自动 seed 默认分类。
**教训**：修数据契约问题时，必须同时检查：代码逻辑 + 数据库 schema + 初始数据。

### 错误 4：端口冲突处理不当
**表现**：反复尝试启动后端在 8000 端口，每次都 `Address already in use`，浪费大量时间。
**原因**：没有先检查端口占用情况（Docker 占用了 8000）。
**修复**：后端改到 8001 端口，前端 proxy 同步修改。
**教训**：启动服务前必须先 `lsof -i :PORT` 检查端口占用。本项目的**后端端口固定为 8001**，不要改回 8000。

### 错误 5：异步 mock 测试语法错误
**表现**：`test_api_crawler.py` 中 mock 异步方法 `SmartCrawler.crawl` 时用了 `mock_crawl.return_value.type(...)`，报错 `TypeError: 'coroutine' object is not callable`。
**原因**：对 Python async mock 不熟悉。
**修复**：使用 `side_effect=mock_crawl_async` 传入 async 函数。
**教训**：mock 异步方法时，用 `side_effect` 传入 async 函数，不要直接设置 `return_value`。

### 错误 6：假设 ORM 有关系属性
**表现**：`articles.py` 的 `_article_to_response` 中直接访问 `article.source.name`，但 `Article` 模型没有定义 `source = relationship("Source")`。
**原因**：SQLAlchemy 不会自动创建关系属性，除非显式定义。
**修复**：手动查询 Source 表获取名称。
**教训**：访问关联数据时，先确认模型是否定义了 `relationship()`，没有就必须手动 JOIN 查询。

### 错误 7：Pydantic 弃用警告
**表现**：使用 `class Config: from_attributes = True`，触发 `PydanticDeprecatedSince20` 警告。
**原因**：Pydantic V2 弃用了 class-based `Config`。
**修复**：改用 `model_config = ConfigDict(from_attributes=True)`。
**教训**：本项目使用 Pydantic V2，永远用 `ConfigDict`，不用 `class Config`。

### 错误 8：新增迁移后未立即应用
**表现**：新增 002 FTS5 迁移后测试失败，`articles_fts` 表不存在。
**原因**：测试用的是实际数据库文件（data/hub.db），不是内存数据库，迁移未应用。
**修复**：手动运行 `alembic upgrade head`。
**教训**：新增迁移文件后，**必须**运行 `alembic upgrade head` 才能生效。测试前检查迁移状态。

---

## 4. 关键技术决策

### 端口分配（固定，不要改）
| 服务 | 端口 | 原因 |
|---|---|---|
| 后端 | **8001** | 8000 被 Docker 占用 |
| 前端 | **5173** | Vite 默认 |

### API Key 配置
- `.env` 中 `OPENAI_API_KEY` 当前为 `dummy`
- **必须配置真实 Key** 才能使用 AI 功能（采集处理、视频转录、问答、关系分析）
- `FIRECRAWL_API_KEY` 是可选的（Jina Reader 免费）

### 数据库
- SQLite 文件：`data/hub.db`
- 迁移文件：`server/src/db/migrations/versions/`
- 当前迁移版本：001（初始）+ 002（FTS5）
- **启动时自动 seed**：categories 表为空时会自动插入 35 个默认分类

### 启动命令
```bash
# 后端
cd server && source ../.env && python3 -m uvicorn src.main:app --reload --port 8001

# 前端
cd web && npm run dev

# 或同时启动
cd server && source ../.env && python3 -m uvicorn src.main:app --reload --port 8001 &
cd web && npm run dev
```

---

## 5. 代码修改规范

### 修改前必查
1. 这个修改是否影响现有测试？→ 运行 `pytest tests/ -v`
2. 前端类型是否一致？→ 运行 `cd web && npx tsc --noEmit`
3. 前端能否构建？→ 运行 `cd web && npm run build`
4. 是否需要更新迁移？→ 如果有 schema 变更，新增 Alembic 迁移
5. 是否需要 seed 数据？→ 如果有新表需要默认数据，更新 `seed.py`

### 修改后必做
1. 所有测试通过（95/95）
2. 前端 TypeScript 编译通过（0 error）
3. 前端 Vite 构建成功
4. 推送到 GitHub：`git push origin main`

### Python 3.9 兼容清单
- ❌ `list[T]` → ✅ `List[T]`
- ❌ `dict[K, V]` → ✅ `Dict[K, V]`
- ❌ `T | None` → ✅ `Optional[T]`
- ❌ `str | int` → ✅ `Union[str, int]`

### Pydantic V2 规范
- ❌ `class Config: ...` → ✅ `model_config = ConfigDict(...)`
- ❌ `Field(..., regex=...)` → ✅ `Field(..., pattern=...)`

---

## 6. 常见调试路径

### 前端"加载中"不动
→ 检查后端是否启动：`curl http://localhost:8001/api/health`
→ 检查前端 proxy 是否指向 8001（不是 8000）

### 前端"not found"
→ 检查后端是否启动
→ 检查 URL 路由是否正确（React Router 刷新需要后端配合）

### AI 处理失败
→ 检查 `.env` 中 `OPENAI_API_KEY` 是否为真实 key
→ 检查 OpenAI 账户余额

### 分类树为空
→ 检查数据库 categories 表是否有数据
→ 如果没有，重启后端触发 seed

### 测试失败
→ 检查是否有端口占用
→ 检查 `.env` 是否配置（dummy 值可以运行测试）
→ 检查是否需要运行 `alembic upgrade head`

---

## 7. 文档索引

| 文档 | 内容 |
|---|---|
| `README.md` | 项目简介和快速开始 |
| `V1 BUG.md` | V1 阶段所有 bug 清单和修复方案 |
| `V1 REPAIR验收方案.md` | V1 修复后的验收标准和用例 |
| `待完成事项.md` | 未实现功能清单（P2 + 远期） |
| `2026-04-20-finance-knowledge-hub-design_final.md` | 完整设计文档（终版） |
| `AGENTS.md`（本文件） | 项目记忆和开发规范 |

---

## 8. 最后更新

- **时间**：2026-04-20
- **状态**：V1 Bug 修复完成，95 测试通过，代码已推送 GitHub
- **用户要求**：暂不实现 OCR 功能
- **当前阻塞项**：`.env` 中 `OPENAI_API_KEY` 为 dummy，需用户配置真实 key
