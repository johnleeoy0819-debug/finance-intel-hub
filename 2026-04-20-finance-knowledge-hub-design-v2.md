# FinanceIntel Hub — 财经智识库系统设计文档

> 版本：v2.0  
> 日期：2026-04-20  
> 状态：待审批  
> 基于 v1.0 审核调整

---

## 0. 用大白话讲清楚这个项目

### 这是个什么东西？

想象你有一个**超级聪明的财经秘书**。

每天，互联网上有成千上万条财经新闻——央行降息了、特斯拉出财报了、新能源又打价格战了……你不可能全部看完，更不可能记住它们之间的关系。

**FinanceIntel Hub（财经智识库）** 就是帮你解决这个问题的工具。它做三件事：

1. **自动收集**：像一个不知疲倦的助手，每隔一段时间就去各大财经网站（新浪财经、36氪、华尔街见闻……）把最新的文章抓回来。你也可以自己上传文件——PDF、Word、视频、电子书，统统能处理。

2. **AI 理解**：收集回来的文章不是堆在那里，而是交给 AI（ChatGPT 那种）去"读懂"——它会：
   - 把文章里的广告和废话去掉，只留干货
   - 写一份几句话的摘要（核心说了啥）
   - 自动分类（这是宏观经济的？还是公司研报？）
   - 提取关键词标签（"降准"、"央行"、"流动性"……）
   - 画一张思维导图（文章结构一目了然）
   - 找出和以前文章的关联（"这篇降准的新闻和上周的货币政策文章有关"）

3. **让你方便地用**：所有处理完的知识通过一个网页界面展示出来，你可以：
   - 看今天新增了哪些重要文章
   - 按分类/标签筛选感兴趣的内容
   - 搜索任何关键词，甚至用一句话描述你想找的内容（语义搜索）
   - 看一张知识图谱——所有文章之间的关联像一张网
   - 问"经济大师"AI 任何经济问题，它会基于你的知识库给出有理有据的回答

### 解决了什么问题？

| 没有这个工具时 | 有了这个工具后 |
|---|---|
| 每天花 2 小时刷财经新闻，看完就忘 | 系统自动收集，AI 帮你看完并写好摘要 |
| 看到一篇分析，想找以前的相关文章，翻半天找不到 | 搜一下或看知识图谱，关联文章自动呈现 |
| 攒了一堆 PDF、视频、电子书，从来没整理过 | 上传就行，AI 自动整理入库 |
| 想写分析报告，要从零搜索素材 | 问"经济大师"，基于你的知识库给出有引用的分析 |

### 它长什么样？

打开浏览器，输入一个网址，你会看到：

- **仪表盘**：今天新增了 23 篇文章，本周累计 156 篇，有 5 篇还在处理中
- **知识库**：所有文章的列表，左侧可以按分类筛选，右上角可以搜索
- **文章详情**：点开一篇文章，能看到原文、AI 摘要、思维导图、相关文章
- **知识图谱**：一张可以拖拽的网络图，展示文章之间的关联
- **数据源管理**：管理你的新闻来源——添加、删除、修改采集频率

### 技术上到底怎么做的？（简单版）

整个系统分三大块，就像一个三层蛋糕：

```
┌─────────────────────┐
│  网页界面（你看到的） │  ← 用 React 做的网页，在浏览器里运行
├─────────────────────┤
│  后台服务（干活的）   │  ← 用 Python 写的程序，处理所有逻辑
├─────────────────────┤
│  数据存储（记东西的） │  ← 数据库 + 文件，保存所有信息
└─────────────────────┘
```

**你需要做的**：在电脑上运行一条命令，三层蛋糕就全部启动了。然后打开浏览器就能用。

---

## 1. V2 审核变更摘要

| 变更项 | V1 问题 | V2 调整 |
|--------|---------|---------|
| 目录结构 | 层级深、命名不统一（`routers/` + `services/`） | 扁平化，统一为 `api/` + `core/`，命名全小写蛇形 |
| Prompt 存储 | `.txt` 文件，无参数校验 | `.yaml` 文件，含版本号和输入参数声明 |
| 数据库演进 | 无迁移机制，改表就崩 | 引入 Alembic 迁移，`schema_version` 表管理 |
| 运行时数据 | `storage/` 和代码同级 | 独立 `data/` 目录，全部 `.gitignore` |
| 启动方式 | `start.sh` 不够清晰 | `Makefile` 统一入口（`make dev` / `make prod`） |
| SKILL 演进 | 静态 Markdown，无版本 | SKILL 带版本头，Prompt 可热更新 |
| 测试 | 未提及 | 加入 `tests/` 目录结构和测试策略 |
| 升级路径 | 未提及 | 新增第 14 节：三阶段升级路线图 |
| 前端状态 | 未指定 | 明确使用 Zustand 轻量状态管理 |
| 配置管理 | 散落在代码里 | 统一 `.env` + `config.py` + Pydantic Settings |

---

## 2. 技术方案（维持方案 A，微调）

| 维度 | 选型 | 理由 |
|------|------|------|
| 后端框架 | FastAPI | 异步、自带文档、生态好 |
| 前端框架 | React 18 + Vite | 快、生态大、TypeScript 友好 |
| 状态管理 | Zustand | 比 Redux 简单 10 倍，够用 |
| 结构化存储 | SQLite（通过 SQLAlchemy） | 零配置、单文件、未来可平滑切 PostgreSQL |
| 向量存储 | ChromaDB | 嵌入式、Python 原生、零配置 |
| 全文搜索 | SQLite FTS5 | 内置、免部署、中文支持 |
| 定时任务 | APScheduler | 内置、够用、不引入额外依赖 |
| ORM | SQLAlchemy 2.0 | 主流、支持迁移、支持切换数据库 |
| 数据库迁移 | Alembic | SQLAlchemy 官方迁移工具 |
| AI 接口 | OpenAI SDK | GPT-4o 主力，gpt-4o-mini 跑量 |
| 采集引擎 | Firecrawl + 自建兜底 | 80% 网页用 Firecrawl，20% 特殊源自建 |

---

## 3. 系统架构

### 3.1 分层架构

```
用户浏览器
    │
    │ HTTP
    ▼
┌──────────────────────────────────────────┐
│           web/ (React + Vite)            │
│  pages → components → hooks → api/      │
└──────────────────┬───────────────────────┘
                   │ REST JSON
                   ▼
┌──────────────────────────────────────────┐
│         server/ (FastAPI + Python)       │
│                                          │
│  api/         ← HTTP 入口，薄薄一层       │
│  core/        ← 业务逻辑，所有重活在这里  │
│  db/          ← 数据模型 + 迁移          │
│  prompts/     ← AI Prompt 模板（YAML）   │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ SQLite │ │ChromaDB│ │ data/  │
   │ 结构化  │ │  向量   │ │ MD文件 │
   └────────┘ └────────┘ └────────┘
                   │
                   ▼
          ┌────────────────┐
          │    外部服务      │
          │ OpenAI API      │
          │ Firecrawl API   │
          │ 财经网站源       │
          └────────────────┘
```

### 3.2 核心设计原则

| 原则 | 做法 |
|------|------|
| **一层只做一件事** | `api/` 只做参数校验和路由；`core/` 只做业务逻辑；`db/` 只管数据 |
| **依赖向内** | `api/` 调用 `core/`，`core/` 调用 `db/`，反过来不行 |
| **配置外置** | 所有可变参数（API Key、采集频率、模型名）放 `.env`，代码里不写死 |
| **数据隔离** | 运行时产生的数据（数据库、文件、向量）全部在 `data/` 下，不混入代码 |
| **Prompt 即配置** | Prompt 是 `.yaml` 文件，改 Prompt 不需要改代码，不需要重启 |

### 3.3 数据流

```
[定时触发 / 手动上传]
        │
        ▼
[采集/解析] ──→ 原始内容
        │
        ▼
[AI 清洗] ──→ 纯净正文（去广告/导航/废话）
        │
        ├──→ [AI 摘要]    ──→ 标题、要点、情感、重要性
        ├──→ [AI 分类]    ──→ 一级分类 + 二级分类
        ├──→ [AI 标签]    ──→ 5-10 个关键词
        ├──→ [AI 导图]    ──→ 层级大纲结构
        ├──→ [Embedding]  ──→ 存入 ChromaDB 向量库
        └──→ [AI 关联]    ──→ 与已有文章建立关系
        │
        ▼
[写入 SQLite] + [写入 .md 文件] + [更新知识图谱]
        │
        ▼
[前端展示：仪表盘 / 知识库 / 图谱 / 搜索]
```

---

## 4. 项目目录结构

```
finance-intel-hub/
│
├── server/                        # 后端（Python）
│   ├── src/                       # 源代码
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 应用入口
│   │   ├── config.py              # Pydantic Settings 配置
│   │   │
│   │   ├── api/                   # API 层：路由 + 请求/响应校验
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py         # /api/crawler/*
│   │   │   ├── articles.py        # /api/articles/*
│   │   │   ├── upload.py          # /api/upload/*
│   │   │   ├── search.py          # /api/search/*
│   │   │   ├── graph.py           # /api/graph/*
│   │   │   └── stats.py           # /api/stats/*
│   │   │
│   │   ├── core/                  # 业务逻辑层：所有重活
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py         # 采集引擎（Firecrawl + 自建）
│   │   │   ├── processor.py       # AI 处理流水线（清洗→摘要→分类→标签）
│   │   │   ├── uploader.py        # 文件上传处理（PDF/视频/EPUB 解析）
│   │   │   ├── search.py          # 搜索服务（FTS + 语义）
│   │   │   ├── graph.py           # 知识图谱构建
│   │   │   └── scheduler.py       # APScheduler 定时任务管理
│   │   │
│   │   ├── db/                    # 数据层
│   │   │   ├── __init__.py
│   │   │   ├── engine.py          # SQLAlchemy 引擎 + 会话管理
│   │   │   ├── models.py          # 所有 ORM 模型
│   │   │   └── migrations/        # Alembic 迁移脚本
│   │   │       ├── env.py
│   │   │       └── versions/      # 每次改表生成一个迁移文件
│   │   │
│   │   └── prompts/               # AI Prompt 模板（YAML）
│   │       ├── v1/                # 按版本管理 Prompt
│   │       │   ├── cleaner.yaml
│   │       │   ├── summarizer.yaml
│   │       │   ├── classifier.yaml
│   │       │   ├── tagger.yaml
│   │       │   ├── mindmap.yaml
│   │       │   ├── relation.yaml
│   │       │   ├── video.yaml
│   │       │   └── publication.yaml
│   │       └── loader.py          # Prompt 加载器（读 YAML、填参数）
│   │
│   ├── tests/                     # 测试
│   │   ├── test_processor.py
│   │   ├── test_crawler.py
│   │   └── test_api.py
│   │
│   ├── alembic.ini                # Alembic 迁移配置
│   ├── pyproject.toml             # Python 项目配置 + 依赖
│   └── requirements.txt           # 依赖清单（兼容 pip install）
│
├── web/                           # 前端（React + TypeScript）
│   ├── src/
│   │   ├── main.tsx               # 应用入口
│   │   ├── App.tsx                # 路由配置
│   │   ├── pages/                 # 页面组件（一个页面一个文件）
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── ArticleDetail.tsx
│   │   │   ├── Graph.tsx
│   │   │   ├── Sources.tsx
│   │   │   └── Upload.tsx
│   │   ├── components/            # 可复用的 UI 组件
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── TagList.tsx
│   │   │   ├── CategoryTree.tsx
│   │   │   ├── MindmapView.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── hooks/                 # 自定义 React Hooks
│   │   │   ├── useArticles.ts
│   │   │   └── useSearch.ts
│   │   ├── api/                   # 后端 API 调用封装
│   │   │   └── client.ts
│   │   ├── store/                 # Zustand 状态管理
│   │   │   └── index.ts
│   │   └── types/                 # TypeScript 类型定义
│   │       └── index.ts
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── data/                          # 运行时数据（.gitignore 忽略）
│   ├── articles/                  # Markdown 文章存储
│   │   └── {YYYY}/{MM}/          # 按年月归档
│   ├── uploads/                   # 用户上传的原始文件
│   ├── chroma/                    # ChromaDB 向量数据
│   └── hub.db                     # SQLite 主数据库
│
├── skills/                        # AI Skill 定义
│   └── econ-master/
│       └── SKILL.md
│
├── docs/                          # 项目文档
│   └── superpowers/specs/         # 设计文档
│
├── .env.example                   # 环境变量模板
├── .gitignore
├── Makefile                       # 统一命令入口
└── README.md
```

### 4.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件夹 | 全小写，单数 | `api/`、`core/`、`db/` |
| Python 文件 | 全小写，蛇形 | `ai_processor.py` → `processor.py` |
| React 页面组件 | 大驼峰 | `Dashboard.tsx`、`ArticleDetail.tsx` |
| React 通用组件 | 大驼峰 | `ArticleCard.tsx`、`TagList.tsx` |
| TypeScript 工具 | 全小写，驼峰 | `useArticles.ts`、`client.ts` |
| API 路径 | 全小写，短横线 | `/api/articles`、`/api/search/semantic` |
| 数据库表 | 全小写，蛇形，复数 | `articles`、`knowledge_edges` |
| 环境变量 | 全大写，下划线 | `OPENAI_API_KEY`、`FIRECRAWL_API_KEY` |

### 4.2 为什么这样分（一句话版）

- **`server/src/api/`**：前端发来的请求到这里"分拣"——只做参数检查和转发，不写业务逻辑
- **`server/src/core/`**：所有真正干活的代码在这里——爬虫、AI 处理、搜索、图谱构建
- **`server/src/db/`**：所有跟数据库打交道的代码在这里——表结构定义、数据库升级脚本
- **`server/src/prompts/`**：给 AI 的"指令模板"，是 YAML 配置文件，改它不需要改代码
- **`web/src/pages/`**：每个页面一个文件，对应浏览器里的一个页面
- **`web/src/components/`**：可以在多个页面复用的"零件"
- **`data/`**：程序运行时产生的所有数据，代码仓库不跟踪它

---

## 5. PRD — 产品需求

### 5.1 功能模块（按优先级排列）

**P0 — 最小可用版本（MVP，先做这些）**

| 模块 | 功能 | 说明 |
|------|------|------|
| 采集引擎 | 定时爬取 + 去重 | Firecrawl 主力，URL+标题哈希去重 |
| AI 处理 | 清洗 + 摘要 + 分类 + 标签 | 四步流水线，每篇文章必经 |
| 知识存储 | SQLite + Markdown + ChromaDB | 三份存储各司其职 |
| Web 前端 | 仪表盘 + 知识库列表 + 文章详情 | 三个核心页面 |
| 搜索 | 全文搜索（FTS5） | 关键词搜索 |
| 数据源管理 | 增删改数据源 + 手动触发 | 管理采集来源 |

**P1 — 增强功能（MVP 跑通后做）**

| 模块 | 功能 | 说明 |
|------|------|------|
| AI 处理 | 思维导图 + 关联分析 | 文章结构化 + 知识关联 |
| 知识图谱 | 力导向图可视化 | 文章关联网络展示 |
| 语义搜索 | 向量相似度搜索 | 用自然语言搜索 |
| 文件上传 | PDF/Word/TXT/EPUB 上传 | 手动导入文件 |
| 视频处理 | Whisper 转录 + 结构化 | 视频内容入库 |
| 文献管理 | 书籍/论文录入 + 章节管理 | 学术内容管理 |

**P2 — 远期功能**

| 模块 | 功能 | 说明 |
|------|------|------|
| 文献引擎 | 论文引用网络 | 论文间引用关系图谱 |
| 批量导入 | 文件夹批量导入 | 一次性大量导入 |
| 经济大师 SKILL | Kimi/CLI AI 助手集成 | 基于知识库的问答 |

### 5.2 预定义分类体系

```
宏观经济
├── 货币政策
├── 财政政策
├── 国际贸易
├── GDP / 就业 / 通胀
└── 全球经济

金融市场
├── 股票市场
├── 债券市场
├── 外汇市场
├── 大宗商品
├── 加密货币
└── 市场策略

行业分析
├── 科技互联网
├── 房地产
├── 制造业
├── 医疗健康
├── 新能源
└── 消费零售

商业模型
├── 商业模式创新
├── 企业战略
├── 投资并购
├── 创业融资
└── 公司治理

公司研究
├── 财报解读
├── 竞争分析
├── 管理层动态
└── 估值分析

监管政策
├── 金融监管
├── 行业监管
├── 反垄断
└── 数据合规
```

> **演进方式**：分类体系存储在 `data/config/categories.yaml` 中，而非写死在代码里。新增/修改分类只需编辑此文件，无需改代码。

---

## 6. Prompt 设计（YAML 格式 + 版本管理）

### 6.1 Prompt 文件规范

每个 Prompt 是一个 `.yaml` 文件，包含：

```yaml
# 每个 Prompt 文件的标准结构
version: 1                        # Prompt 版本号，改了就加 1
name: xxx                         # 唯一名称
description: 一句话说明用途         # 人读的说明
model: gpt-4o-mini                # 默认使用的模型
inputs:                           # 声明需要哪些输入参数
  - name: raw_content
    required: true
    description: 原始网页内容
system: |                         # System Prompt
  你是......
user: |                           # User Prompt 模板（用 {{变量名}} 占位）
  ......
```

> **为什么这样做**：
> - 改 Prompt 不需要改代码，不需要重启服务
> - 有版本号，可以 A/B 测试不同 Prompt 的效果
> - 输入参数有声明，程序可以自动检查"传对了没有"
> - 未来可以在前端做一个"Prompt 管理"页面

### 6.2 内容清洗

```yaml
# server/src/prompts/v1/cleaner.yaml
version: 1
name: content_cleaner
description: 从原始网页中提取纯净的财经文章正文
model: gpt-4o-mini
inputs:
  - name: raw_content
    required: true
    description: 原始网页HTML或文本内容
system: |
  你是一名专业的财经内容编辑。你的任务是从原始网页内容中提取纯净的文章正文。
  
  规则：
  1. 只保留文章核心正文，保留段落结构
  2. 去除广告文案（如"点击关注"、"扫码入群"等）
  3. 去除作者个人介绍和版权声明
  4. 保留数据、图表的文字描述
  5. 输出纯文本，不含HTML标签
  6. 如果内容非财经/经济/商业相关，返回 [IRRELEVANT]
user: |
  原始内容：
  {{raw_content}}
  
  请提取纯净正文：
```

### 6.3 智能摘要

```yaml
# server/src/prompts/v1/summarizer.yaml
version: 1
name: article_summarizer
description: 生成财经文章的结构化摘要
model: gpt-4o
inputs:
  - name: clean_content
    required: true
    description: 清洗后的文章正文
system: |
  你是一名资深财经分析师。请对给定文章生成结构化摘要。
  
  输出格式（严格JSON）：
  {
    "title": "优化后的标题（如无必要保持原样）",
    "summary": "50字内的核心观点概述",
    "key_points": ["3-5条核心要点，每条不超过30字"],
    "entities": ["文中提到的公司/机构/人物/政策名称"],
    "sentiment": "positive|neutral|negative",
    "importance": "high|medium|low"
  }
user: |
  文章内容：
  {{clean_content}}
  
  请生成结构化摘要：
```

### 6.4 自动分类

```yaml
# server/src/prompts/v1/classifier.yaml
version: 1
name: article_classifier
description: 将文章归入预定义分类体系
model: gpt-4o-mini
inputs:
  - name: title
    required: true
  - name: summary
    required: true
  - name: key_points
    required: true
  - name: categories
    required: true
    description: 当前分类体系（从配置文件读取，不写死）
system: |
  你是一名财经内容分类专家。请将文章归入给定分类体系中最匹配的节点。
  
  输出格式（严格JSON）：
  {
    "primary_category": "一级分类",
    "secondary_category": "二级分类",
    "confidence": 0.0-1.0,
    "reason": "分类理由（20字内）"
  }
user: |
  标题：{{title}}
  摘要：{{summary}}
  关键要点：{{key_points}}
  
  分类体系：
  {{categories}}
  
  请分类：
```

### 6.5 标签提取

```yaml
# server/src/prompts/v1/tagger.yaml
version: 1
name: tag_extractor
description: 从财经文章中提取精准关键词标签
model: gpt-4o-mini
inputs:
  - name: title
    required: true
  - name: summary
    required: true
  - name: entities
    required: true
system: |
  从财经文章中提取5-10个精准标签。要求：
  1. 包含关键实体（公司名、政策名、人物）
  2. 包含核心概念（如"量化宽松"、"IPO"、"ESG"）
  3. 标签简洁，2-6个字为佳
  4. 避免过于宽泛的词（如"经济"、"市场"）
  
  输出格式：["标签1", "标签2", ...]
user: |
  标题：{{title}}
  摘要：{{summary}}
  实体：{{entities}}
  
  请提取标签：
```

### 6.6 思维导图

```yaml
# server/src/prompts/v1/mindmap.yaml
version: 1
name: mindmap_generator
description: 将文章转化为思维导图层级结构
model: gpt-4o-mini
inputs:
  - name: title
    required: true
  - name: clean_content
    required: true
system: |
  将财经文章转化为层级化的思维导图结构。
  
  输出格式（Markdown 列表，最多3层）：
  - 核心主题
    - 分支1
      - 要点1
      - 要点2
    - 分支2
      - 要点3
  
  要求：
  1. 不超过8个一级分支
  2. 每个分支下不超过5个要点
  3. 用词精准，不要冗余
  4. 保持文章的逻辑结构
user: |
  标题：{{title}}
  内容：
  {{clean_content}}
  
  请生成思维导图结构：
```

### 6.7 关联分析

```yaml
# server/src/prompts/v1/relation.yaml
version: 1
name: relation_analyzer
description: 分析文章与已有知识库文章之间的关联
model: gpt-4o
inputs:
  - name: current_title
    required: true
  - name: current_summary
    required: true
  - name: current_category
    required: true
  - name: current_tags
    required: true
  - name: existing_articles
    required: true
    description: 已有文章摘要列表（最多20篇）
system: |
  分析当前文章与已有知识库文章之间的关联。
  
  输出格式（严格JSON）：
  {
    "related_articles": [
      {
        "article_id": "相关文章ID",
        "relation_type": "主题关联|因果关联|对比关联|延续关联",
        "strength": 0.0-1.0,
        "reason": "关联理由"
      }
    ],
    "new_insights": "基于已有知识，本文带来的新视角（50字内）"
  }
  
  如果无强关联，related_articles 可为空。
user: |
  当前文章：
  标题：{{current_title}}
  摘要：{{current_summary}}
  分类：{{current_category}}
  标签：{{current_tags}}
  
  已有文章列表：
  {{existing_articles}}
  
  请分析关联：
```

### 6.8 视频内容结构化

```yaml
# server/src/prompts/v1/video.yaml
version: 1
name: video_structurer
description: 将视频转录文本结构化为可阅读的知识文档
model: gpt-4o
inputs:
  - name: transcript_segments
    required: true
    description: 视频转录内容（含时间戳分段）
system: |
  你是一名财经视频内容分析师。给定视频转录文本及其时间戳分段，
  请将其结构化为可阅读的知识文档。
  
  规则：
  1. 根据内容逻辑将视频划分为3-6个主题章节
  2. 每个章节给出：标题、时间范围、核心内容摘要
  3. 提取视频中提到的所有数据、观点、预测
  4. 标注关键时间戳，方便回溯原视频
  5. 如果内容非财经相关，返回 [IRRELEVANT]
  
  输出格式（严格JSON）：
  {
    "title": "视频主题标题",
    "overall_summary": "整体概述（50字）",
    "chapters": [
      {
        "title": "章节标题",
        "start_time": "00:00:00",
        "end_time": "00:05:30",
        "summary": "章节摘要",
        "key_points": ["要点1", "要点2"]
      }
    ],
    "entities": ["提到的实体"],
    "sentiment": "positive|neutral|negative"
  }
user: |
  视频转录内容（含时间戳）：
  {{transcript_segments}}
  
  请结构化：
```

### 6.9 文献/书籍解析

```yaml
# server/src/prompts/v1/publication.yaml
version: 1
name: publication_parser
description: 对书籍章节或论文进行深度解析
model: gpt-4o
inputs:
  - name: content
    required: true
  - name: pub_type
    required: true
    description: "book_chapter | paper | report"
  - name: title
    required: true
  - name: authors
    required: true
system: |
  你是一名学术文献分析专家。请对给定的书籍章节或论文内容进行深度解析。
  
  输出格式（严格JSON）：
  {
    "title": "章节/论文标题",
    "summary": "核心论点概述（100字）",
    "key_arguments": ["核心论点1", "核心论点2", "核心论点3"],
    "methodology": "研究方法（如适用）",
    "evidence": ["关键证据/数据"],
    "conclusions": ["结论1", "结论2"],
    "practical_implications": "实践意义（50字）",
    "related_theories": ["相关理论/模型"],
    "tags": ["标签1", "标签2"],
    "academic_value": "high|medium|low"
  }
user: |
  文献内容：
  {{content}}
  
  文献类型：{{pub_type}}
  标题：{{title}}
  作者：{{authors}}
  
  请深度解析：
```

---

## 7. 数据库设计（支持迁移演进）

### 7.1 迁移策略

```
改表流程：
1. 修改 server/src/db/models.py 中的 ORM 模型
2. 运行 `make db-migrate msg="添加xxx字段"` 自动生成迁移脚本
3. 运行 `make db-upgrade` 执行迁移
4. 迁移脚本永久保留在 server/src/db/migrations/versions/ 中

好处：
- 每次改表都有记录，可以回退
- 多人协作不会冲突
- 未来切换到 PostgreSQL 时，迁移脚本自动适配
```

### 7.2 SQLite 表结构

```sql
-- ============================================================
-- 系统元数据
-- ============================================================

-- 分类体系配置（可从 YAML 同步，也可在前端编辑）
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,       -- 英文标识：如 "macro_economy"
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 采集相关
-- ============================================================

-- 数据源配置
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    driver TEXT NOT NULL DEFAULT 'firecrawl',  -- firecrawl | rss | api | custom
    config TEXT,                     -- JSON：采集参数
    schedule TEXT,                   -- cron 表达式：如 "0 */2 * * *"
    is_active INTEGER DEFAULT 1,
    last_crawled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 文章核心
-- ============================================================

-- 文章主表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    url TEXT UNIQUE,                 -- 原文URL（上传文件可为空）
    title TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,

    -- AI 处理结果
    clean_content TEXT,
    summary TEXT,
    key_points TEXT,                 -- JSON 数组
    entities TEXT,                   -- JSON 数组
    sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')),
    importance TEXT CHECK(importance IN ('high', 'medium', 'low')),
    mindmap TEXT,                    -- Markdown 层级列表

    -- 分类（外键关联 categories 表）
    primary_category_id INTEGER REFERENCES categories(id),
    secondary_category_id INTEGER REFERENCES categories(id),

    -- 存储路径
    md_file_path TEXT,

    -- 状态机
    status TEXT DEFAULT 'pending' CHECK(status IN (
        'pending', 'crawled', 'cleaning', 'processing', 'completed', 'failed'
    )),
    error_message TEXT,              -- 失败时的错误信息

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文章-标签关联（多对多）
CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- 知识图谱边（文章间的关联关系）
CREATE TABLE knowledge_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    target_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL CHECK(relation_type IN (
        '主题关联', '因果关联', '对比关联', '延续关联'
    )),
    strength REAL CHECK(strength >= 0 AND strength <= 1),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_article_id, target_article_id, relation_type)
);

-- 全文搜索索引
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, clean_content,
    content='articles',
    content_rowid='id'
);

-- ============================================================
-- 文件上传
-- ============================================================

CREATE TABLE upload_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK(file_type IN (
        'pdf', 'docx', 'txt', 'epub', 'image', 'video'
    )),
    file_size INTEGER,
    status TEXT DEFAULT 'pending' CHECK(status IN (
        'pending', 'processing', 'completed', 'failed'
    )),
    error_message TEXT,
    article_id INTEGER REFERENCES articles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- ============================================================
-- 视频转录（P1）
-- ============================================================

CREATE TABLE video_transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_path TEXT NOT NULL,
    audio_path TEXT,
    transcript_text TEXT,
    segments TEXT,                    -- JSON: [{start, end, text}, ...]
    language TEXT DEFAULT 'zh',
    model_used TEXT DEFAULT 'whisper-1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 文献管理（P1）
-- ============================================================

CREATE TABLE publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pub_type TEXT NOT NULL CHECK(pub_type IN ('book', 'paper', 'report')),
    title TEXT NOT NULL,
    authors TEXT,                     -- JSON 数组
    publisher TEXT,
    isbn TEXT,
    doi TEXT,
    url TEXT,
    abstract TEXT,
    keywords TEXT,                    -- JSON 数组
    publication_date TEXT,
    file_path TEXT,
    source TEXT,
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE publication_chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_id INTEGER REFERENCES publications(id) ON DELETE CASCADE,
    chapter_number INTEGER,
    title TEXT NOT NULL,
    summary TEXT,
    start_page INTEGER,
    end_page INTEGER,
    content_text TEXT,
    md_file_path TEXT,
    article_id INTEGER REFERENCES articles(id)  -- 关联到 articles 表，复用搜索/图谱
);

-- ============================================================
-- 索引（查询性能）
-- ============================================================

CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_primary_category ON articles(primary_category_id);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_importance ON articles(importance);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_sources_is_active ON sources(is_active);
```

### 7.3 V1 → V2 数据库变更说明

| 变更 | 理由 |
|------|------|
| 分类从文本字段改为外键关联 `categories` 表 | 分类体系可在数据库中管理，支持动态增删，不写死 |
| `articles.status` 增加更多状态 | 让流水线每一步的状态可追踪：`pending → crawled → cleaning → processing → completed` |
| 增加 `articles.error_message` | 失败时有据可查 |
| 增加 `articles.mindmap` | 思维导图存数据库而非单独文件，查询更方便 |
| 增加 `CHECK` 约束 | 数据库层面保证数据合法性 |
| 增加索引 | 常用查询字段建索引，列表页和筛选不会慢 |
| `publication_chapters` 增加 `article_id` | 书籍章节关联到 articles 表，可以复用搜索和知识图谱 |

### 7.4 Markdown 文件格式（不变）

路径：`data/articles/{YYYY}/{MM}/{article_id}.md`

```markdown
---
id: 42
title: "央行宣布降准0.5个百分点"
url: "https://finance.sina.com.cn/..."
source: "新浪财经"
author: "张三"
published_at: "2026-04-20T09:00:00"
created_at: "2026-04-20T10:30:00"
category:
  primary: "宏观经济"
  secondary: "货币政策"
tags: ["降准", "央行", "流动性", "LPR", "货币政策"]
sentiment: "positive"
importance: "high"
entities: ["中国人民银行", "LPR"]
related_articles: [15, 23, 38]
---

# 央行宣布降准0.5个百分点

## AI摘要

- 央行决定于2026年4月25日下调金融机构存款准备金率0.5个百分点
- 此次降准将释放长期资金约1万亿元
- 旨在降低实体经济融资成本，支持稳增长

## 思维导图

- 降准政策
  - 政策内容
    - 降准0.5个百分点
    - 释放资金1万亿
  - 市场影响
    - 流动性改善
    - LPR下行预期

## 正文

[清洗后的完整正文...]
```

---

## 8. API 设计

```yaml
# ── 采集 ────────────────────────────────
POST   /api/crawler/sources           # 新增数据源
GET    /api/crawler/sources           # 获取所有数据源
PUT    /api/crawler/sources/{id}      # 更新数据源
DELETE /api/crawler/sources/{id}      # 删除数据源
POST   /api/crawler/trigger/{id}      # 手动触发某个源的采集

# ── 文章 ────────────────────────────────
GET    /api/articles                  # 文章列表（分页 + 筛选）
GET    /api/articles/{id}             # 文章详情
DELETE /api/articles/{id}             # 删除文章
GET    /api/articles/{id}/related     # 获取关联文章

# ── 上传 ────────────────────────────────
POST   /api/upload                    # 上传文件
GET    /api/upload/tasks              # 上传任务列表
GET    /api/upload/tasks/{id}         # 上传任务状态

# ── 分类与标签 ──────────────────────────
GET    /api/categories                # 分类树
GET    /api/tags                      # 标签列表（按使用频率排序）
GET    /api/tags/{name}/articles      # 某标签下的文章

# ── 搜索 ────────────────────────────────
GET    /api/search?q={keyword}        # 全文搜索
GET    /api/search/semantic?q={text}  # 语义搜索（P1）

# ── 知识图谱 ────────────────────────────
GET    /api/graph/nodes               # 图谱节点
GET    /api/graph/edges               # 图谱边
GET    /api/graph/subgraph?article_id={id}&depth={n}  # 子图

# ── 统计 ────────────────────────────────
GET    /api/stats/dashboard           # 仪表盘汇总数据
```

---

## 9. 前端页面设计

### 9.1 页面路由

| 页面 | 路径 | 文件 | 说明 |
|------|------|------|------|
| 仪表盘 | `/` | `Dashboard.tsx` | 统计概览 |
| 知识库 | `/library` | `Library.tsx` | 文章列表 + 筛选 |
| 文章详情 | `/article/:id` | `ArticleDetail.tsx` | 原文/摘要/导图/关联 |
| 知识图谱 | `/graph` | `Graph.tsx` | 可视化网络（P1） |
| 数据源 | `/sources` | `Sources.tsx` | 采集源管理 |
| 上传中心 | `/upload` | `Upload.tsx` | 文件上传（P1） |

### 9.2 仪表盘

```
┌──────────────────────────────────────────────────────────┐
│  FinanceIntel Hub                    [搜索] [设置] [刷新] │
├──────────────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                 │
│  │今日新增│  │本周累计│  │ 待处理 │  │ 数据源 │                │
│  │  23   │  │  156  │  │   5   │  │   8   │                │
│  └──────┘  └──────┘  └──────┘  └──────┘                 │
├──────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐                  │
│  │  分类分布饼图    │  │  采集趋势折线图  │                  │
│  │                │  │                │                  │
│  └────────────────┘  └────────────────┘                  │
├──────────────────────────────────────────────────────────┤
│  最新入库                                                 │
│  ┌──────────────────────────────────────────────────────┐│
│  │ 央行宣布降准0.5个百分点    宏观经济/货币政策   10分钟前 ││
│  │ 特斯拉Q1财报超预期         公司研究/财报解读   32分钟前 ││
│  │ 新能源车企价格战加剧       行业分析/新能源     1小时前  ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

### 9.3 知识库列表

```
┌──────────────────────────────────────────────────────────┐
│  FinanceIntel Hub    [搜索文章、标签...]         [筛选 ▼] │
├──────────┬───────────────────────────────────────────────┤
│          │  全部文章 (156)    [最新 ▼] [列表 | 卡片]     │
│ 分类      │                                              │
│ ▸ 宏观经济│  ┌──────────────────────────────────────────┐ │
│ ▸ 金融市场│  │ 央行宣布降准0.5个百分点                    │ │
│ ▸ 行业分析│  │ #降准 #央行 #流动性  宏观经济/货币政策     │ │
│ ▸ 商业模型│  │ 央行决定于2026年4月25日下调金融机...       │ │
│ ▸ 公司研究│  │ 😊 正面  ⭐ 高   10分钟前                │ │
│ ▸ 监管政策│  └──────────────────────────────────────────┘ │
│          │  ┌──────────────────────────────────────────┐ │
│ 热门标签  │  │ 特斯拉Q1财报超预期                        │ │
│ #降准     │  │ #特斯拉 #财报 #电动车  公司研究/财报解读   │ │
│ #美联储   │  │ 特斯拉发布2026年第一季度财报...           │ │
│ #人工智能 │  │ 😊 正面  ⭐ 高   32分钟前                │ │
│          │  └──────────────────────────────────────────┘ │
│          │                                              │
│          │  ◀ 1  2  3 ... 10 ▶                          │
└──────────┴───────────────────────────────────────────────┘
```

### 9.4 文章详情

```
┌──────────────────────────────────────────────────────────┐
│  ← 返回知识库     央行宣布降准0.5个百分点        [操作 ▼] │
├──────────────────────────────────────────────────────────┤
│  宏观经济 › 货币政策    #降准 #央行 #流动性 #LPR          │
│  新浪财经  张三  2026-04-20                              │
├──────────────────────────────────────────────────────────┤
│  [ AI摘要 ] [ 原文 ] [ 思维导图 ] [ 关联文章 ]           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  核心观点：央行降准0.5个百分点，释放长期资金约1万亿元      │
│                                                          │
│  关键要点：                                               │
│  • 降准0.5个百分点，4月25日生效                            │
│  • 释放长期资金约1万亿元                                  │
│  • 降低实体经济融资成本                                   │
│  • 市场预期LPR跟随下调                                    │
│                                                          │
│  涉及实体：中国人民银行、LPR                              │
│  情感倾向：😊 正面   重要程度：⭐ 高                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 9.5 知识图谱

```
┌──────────────────────────────────────────────────────────┐
│  知识图谱                                  [力导图 | 环形] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                  [央行降准]                               │
│                     │                                    │
│        ┌────────────┼────────────┐                       │
│        │            │            │                       │
│   [货币政策]───[LPR下调]───[银行股]                       │
│        │                         │                       │
│   [经济数据]                [实体经济]                    │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  选中：央行降准                                           │
│  分类：宏观经济/货币政策   标签：降准 央行 流动性          │
│  [查看详情]  [查看关联]                                   │
└──────────────────────────────────────────────────────────┘
```

### 9.6 数据源管理

```
┌──────────────────────────────────────────────────────────┐
│  数据源管理                                 [+ 新增数据源] │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐│
│  │ 新浪财经              [编辑] [删除] [立即采集]        ││
│  │ https://finance.sina.com.cn  firecrawl  每2小时      ││
│  │ 上次采集：5分钟前  状态：✅ 正常                      ││
│  ├──────────────────────────────────────────────────────┤│
│  │ 36氪                  [编辑] [删除] [立即采集]        ││
│  │ https://36kr.com  rss  每小时                        ││
│  │ 上次采集：12分钟前  状态：✅ 正常                     ││
│  ├──────────────────────────────────────────────────────┤│
│  │ 华尔街见闻            [编辑] [删除] [立即采集]        ││
│  │ https://wallstreetcn.com  firecrawl  每2小时         ││
│  │ 上次采集：1小时前  状态：✅ 正常                      ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 10. Firecrawl 采集方案

### 10.1 双驱动架构

```
采集引擎 (core/crawler.py)
│
├── FirecrawlDriver（主力，处理80%的来源）
│   ├── 输入：URL 或站点地图
│   ├── 输出：干净 Markdown + 标题/作者/时间
│   └── 适用：新闻站、博客、资讯页面
│
└── CustomDriver（兜底，处理20%的特殊源）
    ├── RSSParser（RSS/Atom 源）
    ├── APIClient（有开放 API 的平台）
    └── RawScraper（其他特殊情况）
```

### 10.2 数据源配置示例

```json
{
  "name": "新浪财经-宏观",
  "driver": "firecrawl",
  "config": {
    "url": "https://finance.sina.com.cn/china/",
    "limit": 20,
    "includePaths": ["/china/*"],
    "excludePaths": ["/china/gjcj/*"],
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  },
  "schedule": "0 */2 * * *"
}
```

### 10.3 成本控制

| Firecrawl 方案 | 费用 | credits/月 | 建议场景 |
|---|---|---|---|
| Free | 免费 | 500 | 开发测试 |
| Pro | $19/月 | 5,000 | 个人使用 |
| Scale | $249/月 | 50,000 | 团队/高频 |

策略：设置每日 credit 上限，Firecrawl 处理标准网页，RSS/API 处理免费源。

---

## 11. 核心流水线

### 11.1 文章处理流水线（伪代码）

```python
async def process_article(raw_html: str, source_url: str) -> int | None:
    """一篇文章从采集到入库的完整流程"""

    # 1. 去重
    if await is_duplicate(source_url):
        return None

    # 2. AI 清洗
    article = await db.create_article(url=source_url, status="crawled")
    clean = await ai.run_prompt("cleaner", raw_content=raw_html)
    if clean == "[IRRELEVANT]":
        await db.update_status(article.id, "failed", error="内容不相关")
        return None

    await db.update_status(article.id, "cleaning")

    # 3. AI 处理（摘要 + 分类 + 标签 可并行）
    await db.update_status(article.id, "processing")
    summary, category, tags = await asyncio.gather(
        ai.run_prompt("summarizer", clean_content=clean),
        ai.run_prompt("classifier", title=..., summary=..., categories=...),
        ai.run_prompt("tagger", title=..., summary=..., entities=...),
    )

    # 4. 思维导图（P1，可选）
    mindmap = await ai.run_prompt("mindmap", title=..., clean_content=clean)

    # 5. Embedding → ChromaDB
    await vector_store.add(article.id, clean)

    # 6. 关联分析（P1，可选）
    relations = await ai.run_prompt("relation", ...)

    # 7. 写入数据库 + Markdown 文件
    await db.save_full_article(article.id, clean, summary, category, tags, mindmap)
    await save_markdown_file(article.id, ...)
    await db.save_relations(article.id, relations)

    await db.update_status(article.id, "completed")
    return article.id
```

### 11.2 文章状态机

```
pending → crawled → cleaning → processing → completed
                                    ↘
                                   failed（任何步骤失败都跳到这里）
```

---

## 12. "经济大师" SKILL（v2）

### 12.1 SKILL.md

```markdown
---
name: econ-master
version: 2
description: 基于本地财经知识库的经济分析助手
api_base: http://localhost:8000/api
---

# 经济大师模式

## 身份

你是 FinanceIntel Hub 首席经济分析师。你可以访问用户的本地财经知识库。

## 工作流

1. **解析问题** → 确定时间范围、分析深度、涉及领域
2. **检索知识库** → 调用 API 获取相关文章
3. **整合证据** → 按权重排序检索结果
4. **生成回答** → 使用模板输出结构化分析

## 检索方式

```
GET {api_base}/search/semantic?q={用户问题}&limit=10
GET {api_base}/search?q={关键词}&limit=5
GET {api_base}/graph/subgraph?article_id={id}&depth=2
```

## 回答模板

### 核心判断
[一句话核心观点]

### 分析框架
- 维度1
  - 论点（引用：文章标题 日期 #ID）
- 维度2
  - 论点（引用：文章标题 日期 #ID）

### 数据与事实
- 数据1：数值（来源）

### 风险提示
[基于历史案例的风险警示]

### 延伸阅读
[推荐3-5篇相关文章]

## 约束

1. 不引用知识库中不存在的内容
2. 区分"最新数据"和"历史数据"
3. 预测性观点标注置信度（高/中/低）
4. 矛盾观点必须呈现双方论据

## 特殊指令

- `/deep` — 深度分析，检索20+篇，3000字以上
- `/compare` — 对比分析
- `/timeline` — 时间线梳理
- `/paper` — 学术模式，优先引用论文
```

### 12.2 SKILL 演进机制

- SKILL.md 头部有 `version` 字段，每次修改递增
- `api_base` 可配置，支持本地和远程部署
- 检索方式和回答模板可独立更新，不影响系统代码
- 未来可做多个 SKILL 变体（如 `econ-master-lite`、`econ-master-research`）

---

## 13. 配置与启动

### 13.1 环境变量 (.env.example)

```bash
# AI 服务
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL_PRIMARY=gpt-4o          # 主力模型（摘要/关联分析）
OPENAI_MODEL_FAST=gpt-4o-mini        # 快速模型（清洗/分类/标签）

# 采集服务
FIRECRAWL_API_KEY=fc-xxx

# 数据存储
DATA_DIR=./data                       # 运行时数据目录
DATABASE_URL=sqlite:///./data/hub.db  # 数据库路径

# 服务端口
SERVER_PORT=8000
```

### 13.2 Makefile 统一入口

```makefile
# ── 开发 ─────────────────────────
dev:          ## 启动开发环境（后端 + 前端）
	@echo "启动后端..."
	cd server && uvicorn src.main:app --reload --port 8000 &
	@echo "启动前端..."
	cd web && npm run dev

# ── 数据库 ───────────────────────
db-migrate:   ## 生成迁移脚本（改了 models.py 后运行）
	cd server && alembic revision --autogenerate -m "$(msg)"

db-upgrade:   ## 执行数据库迁移
	cd server && alembic upgrade head

db-reset:     ## 重置数据库（危险！）
	rm -f data/hub.db && cd server && alembic upgrade head

# ── 安装 ─────────────────────────
install:      ## 安装所有依赖
	cd server && pip install -r requirements.txt
	cd web && npm install

# ── 测试 ─────────────────────────
test:         ## 运行后端测试
	cd server && pytest tests/ -v

# ── 生产 ─────────────────────────
build:        ## 构建前端
	cd web && npm run build

prod:         ## 生产模式启动
	cd server && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 13.3 用大白话说启动方式

```
第一次使用：
1. 复制 .env.example 为 .env，填入你的 API Key
2. 运行 make install   ← 安装所有依赖
3. 运行 make db-upgrade ← 创建数据库
4. 运行 make dev        ← 启动！

之后每次使用：
1. 运行 make dev        ← 一条命令搞定
2. 打开浏览器访问 http://localhost:5173
```

---

## 14. 升级路线图

### 阶段一：MVP（当前 → 第 2-3 周）

**目标**：跑通核心流程——采集 → AI 处理 → 存储 → 展示

```
做什么：
✅ 后端：FastAPI + SQLite + ChromaDB
✅ 采集：Firecrawl 对接 2-3 个财经源
✅ AI：清洗 + 摘要 + 分类 + 标签（四步流水线）
✅ 前端：仪表盘 + 知识库列表 + 文章详情（三个核心页面）
✅ 搜索：全文搜索（FTS5）
✅ 数据源管理页面

不做什么：
❌ 知识图谱可视化
❌ 语义搜索
❌ 文件上传
❌ 视频处理
❌ 文献管理
❌ 经济大师 SKILL
```

### 阶段二：增强（第 3-5 周）

**目标**：知识关联 + 多源输入 + 智能搜索

```
新增：
✅ 思维导图生成 + markmap 渲染
✅ 关联分析 + 知识图谱可视化（D3.js 力导向图）
✅ 语义搜索（ChromaDB 向量检索）
✅ 文件上传（PDF / Word / TXT / EPUB）
✅ 视频处理（Whisper 转录 + 结构化）
✅ 更多采集源

架构不变，只加功能。
```

### 阶段三：智能化（第 5-8 周）

**目标**：知识库变成智能助手

```
新增：
✅ 经济大师 SKILL 上线
✅ 文献管理（书籍 / 论文）
✅ 批量导入
✅ Prompt 版本管理和 A/B 测试
✅ 用户手动修正分类/标签，反馈优化 Prompt

可选的架构升级（按需）：
🔄 SQLite → PostgreSQL（数据量大了再切）
🔄 单进程 → 后台任务队列（处理量大了再切）
🔄 Docker 化部署
```

### 未来可能的方向

| 方向 | 说明 | 前提条件 |
|------|------|----------|
| PostgreSQL 迁移 | 数据量超过 10 万篇或需要多用户并发 | 改 `.env` 中的 `DATABASE_URL`，运行 `make db-upgrade` |
| 后台任务队列 | AI 处理量大，前端响应变慢 | 引入 Celery + Redis |
| 多用户支持 | 从个人工具变成团队工具 | 加 `users` 表 + JWT 认证 |
| 插件系统 | 新数据源类型频繁增加 | `core/crawler.py` 改为插件注册机制 |
| 移动端 | 手机上看知识库 | 前端做响应式适配 |

---

## 15. 技术风险与规避

| 风险 | 规避措施 |
|------|----------|
| 爬虫被封 IP | 控制频率、Firecrawl 自带反封机制、遵守 robots.txt |
| AI API 费用过高 | gpt-4o-mini 处理清洗/分类/标签；gpt-4o 只用于摘要/关联；设每日上限 |
| 文章去重不准 | URL 精确匹配 + 标题相似度双重校验 |
| AI 分类不准 | 用户可手动修正，修正记录可用于 Few-shot 优化 Prompt |
| 向量数据库膨胀 | 定期归档，按月分 Collection |
| 数据库表结构改了旧数据怎么办 | Alembic 迁移：每次改表自动生成升级脚本，老数据自动适配 |

---

## 16. 测试策略

```
测试什么：                      不测什么：
✅ AI Prompt 输出格式是否正确    ❌ 第三方库内部逻辑
✅ 流水线状态流转是否正确        ❌ 前端 UI 样式
✅ 去重逻辑是否有效
✅ API 入参校验是否正确
✅ 数据库迁移是否能跑通
```

目录：`server/tests/`，使用 `pytest`，运行 `make test`。

---

*V2 设计文档完成。主要变更：目录结构扁平化、数据库支持迁移演进、Prompt YAML 化+版本管理、新增升级路线图、新增大白话解释。*
