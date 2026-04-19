# FinanceIntel Hub — 财经智识库系统设计文档（终版）

> 版本：Final  
> 日期：2026-04-20  
> 状态：已审批  
> 来源：整合 v1.1（Kimi）+ v2.0（Claude）+ v2.1（Claude）最优部分

---

## 1. 用大白话讲清楚这个项目

### 这是个什么东西？

想象你有一个**超级聪明的财经秘书**。

每天，互联网上有成千上万条财经新闻——央行降息了、特斯拉出财报了、新能源又打价格战了……你不可能全部看完，更不可能记住它们之间的关系。

**FinanceIntel Hub（财经智识库）** 就是帮你解决这个问题的工具。它做三件事：

1. **自动收集**：每隔一段时间就去各大财经网站把最新的文章抓回来。你也可以自己上传文件——PDF、Word、视频、电子书，统统能处理。

2. **AI 理解**：收集回来的文章交给 AI 去"读懂"——去广告、写摘要、自动分类、提取标签、画思维导图、找出和以前文章的关联。

3. **让你方便地用**：通过网页界面展示所有知识，你可以看热点、搜关键词、看知识图谱、问"经济大师"AI 任何问题——它会基于你的知识库给出有理有据的回答，而且这个大师会越用越懂你。

### 解决了什么问题？

| 没有这个工具时 | 有了这个工具后 |
|---|---|
| 每天花 2 小时刷财经新闻，看完就忘 | 系统自动收集，AI 帮你看完并写好摘要 |
| 看到一篇分析，想找以前的相关文章，翻半天找不到 | 搜一下或看知识图谱，关联文章自动呈现 |
| 攒了一堆 PDF、视频、电子书，从来没整理过 | 上传就行，AI 自动整理入库 |
| 想写分析报告，要从零搜索素材 | 问"经济大师"，基于你的知识库给出带引用的分析 |
| AI 回答千篇一律，不贴合你的关注点 | SKILL 进化机制让 AI 越用越懂你的偏好 |

### MVP 长什么样？

打开浏览器，看到一个网页：

- **仪表盘**：今天新增了 23 篇文章，本周累计 156 篇，热点分布一目了然
- **知识库**：所有文章的列表，左侧按二级分类筛选，右上角搜索
- **文章详情**：原文、AI 摘要、思维导图、关联文章，一个页面看完
- **上传中心**：拖拽上传 PDF/Word/视频/EPUB，自动处理入库
- **数据源管理**：管理你的新闻来源——添加、删除、修改采集频率

**以后还会加上**：知识图谱可视化、PWA 手机应用、云端同步、多领域扩展。

---

## 2. 设计原则：MVP 最小可用 + 预留扩展点

Claude 的 v2.1 很多设计是为"未来升级"准备的，这导致 MVP 负担过重。**本终版严格区分四档**:

| 档位 | 定义 | 当前决策 |
|------|------|----------|
| **MVP（必须做）** | 没有它系统跑不通 | Web 端 + 采集 + AI 处理 + 搜索 + 上传 + SKILL 基础版 |
| **P1（紧接着做）** | 有它体验大幅提升 | 图谱 + 语义搜索 + 视频 + 文献 + SKILL 进化 |
| **P2（有余力做）** | 锦上添花 | PWA + A/B 测试 + 用户记忆精细化 |
| **远期（以后再说）** | 商业化/规模化才需要 | 云端迁移 + App + 多领域 + 多用户 |

**核心原则**：
- 每个功能实现时，**接口和抽象层**要预留扩展点（Claude 说得对）
- 但**具体实现**只做到当前档位需要的最小程度（Claude 过度了）
- 代码里不写死任何配置，全部外置到 `.env`

---

## 3. 技术方案

| 维度 | 选型 | 理由 |
|------|------|------|
| 后端框架 | FastAPI | 异步、自带文档、生态好 |
| 前端框架 | React 18 + Vite | 快、生态大、TypeScript 友好 |
| 状态管理 | Zustand | 比 Redux 简单 10 倍，够用 |
| 样式方案 | TailwindCSS | 响应式原生支持，MVP 就能适配手机浏览器 |
| 结构化存储 | SQLite（SQLAlchemy 2.0） | 零配置、单文件，未来改 `DATABASE_URL` 平滑切 PostgreSQL |
| 向量存储 | ChromaDB | 嵌入式、Python 原生、零配置 |
| 全文搜索 | SQLite FTS5 | 内置、免部署、中文支持 |
| 定时任务 | APScheduler | 内置、够用，处理量大了再切 Celery |
| ORM | SQLAlchemy 2.0 | 主流、支持 Alembic 迁移、数据库可切换 |
| 数据库迁移 | Alembic | 改表自动生成脚本，老数据自动适配 |
| AI 接口 | OpenAI SDK | GPT-4o 主力，gpt-4o-mini 跑量 |
| 采集引擎 | Firecrawl + 自建兜底 | 80% 网页用 Firecrawl，20% 特殊源自建 |
| 语音转录 | OpenAI Whisper API | 效果最佳，本地 Whisper 作为备选 |

---

## 4. 系统架构

### 4.1 分层架构

```
用户浏览器（桌面 + 手机）
    │
    │ HTTP
    ▼
┌──────────────────────────────────────────┐
│           web/ (React + Vite)            │
│  pages → components → hooks → api/      │
│  TailwindCSS 响应式 — MVP 就能手机看      │
└──────────────────┬───────────────────────┘
                   │ REST JSON
                   ▼
┌──────────────────────────────────────────┐
│         server/ (FastAPI + Python)       │
│                                          │
│  api/         ← HTTP 入口，参数校验       │
│  core/        ← 业务逻辑，所有重活        │
│  db/          ← 数据模型 + Alembic 迁移   │
│  prompts/     ← AI Prompt 模板（YAML）    │
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
          │ Whisper API     │
          │ 财经网站源       │
          └────────────────┘
```

### 4.2 核心设计原则

| 原则 | 做法 |
|------|------|
| **一层只做一件事** | `api/` 只做参数校验和路由；`core/` 只做业务逻辑；`db/` 只管数据 |
| **依赖向内** | `api/` 调用 `core/`，`core/` 调用 `db/`，反过来不行 |
| **配置外置** | 所有可变参数放 `.env`，代码里不写死 |
| **数据隔离** | 运行时数据全部在 `data/` 下，不混入代码 |
| **Prompt 即配置** | Prompt 是 `.yaml` 文件，改 Prompt 不需要改代码，不需要重启 |
| **抽象预留扩展** | 存储层用 `StorageBackend` 接口，现在只实现本地，以后可接 S3 |

### 4.3 数据流

```
[定时触发 / 手动上传 / 文件导入]
        │
        ▼
[采集/解析] ──→ 原始内容
        │
        ▼
[AI 清洗] ──→ 纯净正文
        │
        ├──→ [AI 摘要]    ──→ 标题、要点、情感、重要性
        ├──→ [AI 分类]    ──→ 一级分类 + 二级分类（不突破二级）
        ├──→ [AI 标签]    ──→ 5-10 个关键词（承载三级细分）
        ├──→ [AI 导图]    ──→ 层级大纲结构
        ├──→ [Embedding]  ──→ 存入 ChromaDB
        └──→ [AI 关联]    ──→ 与已有文章建立关系
        │
        ▼
[写入 SQLite] + [写入 .md 文件] + [更新知识图谱]
        │
        ▼
[前端展示：仪表盘 / 知识库 / 图谱 / 搜索 / 上传]
        │
        ▼
[SKILL 调用：语义检索 → 整合证据 → 生成回答 → 收集反馈 → 进化迭代]
```

---

## 5. 项目目录结构

```
finance-intel-hub/
│
├── server/                        # 后端（Python）
│   ├── src/
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
│   │   │   ├── stats.py           # /api/stats/*
│   │   │   ├── skill.py           # /api/skill/*  — SKILL 反馈/记忆
│   │   │   └── domains.py         # /api/domains/* — 知识领域（预留）
│   │   │
│   │   ├── core/                  # 业务逻辑层：所有重活
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py         # 采集引擎（Firecrawl + 自建）
│   │   │   ├── processor.py       # AI 处理流水线
│   │   │   ├── uploader.py        # 文件上传处理
│   │   │   ├── search.py          # 搜索服务（FTS + 语义）
│   │   │   ├── graph.py           # 知识图谱构建
│   │   │   ├── scheduler.py       # APScheduler 定时任务
│   │   │   ├── feedback.py        # 反馈收集 + Few-shot 样本管理
│   │   │   ├── memory.py          # 用户记忆管理
│   │   │   └── storage.py         # 存储抽象层（本地/S3 接口）
│   │   │
│   │   ├── db/                    # 数据层
│   │   │   ├── __init__.py
│   │   │   ├── engine.py          # SQLAlchemy 引擎
│   │   │   ├── models.py          # ORM 模型
│   │   │   └── migrations/        # Alembic 迁移脚本
│   │   │       ├── env.py
│   │   │       └── versions/
│   │   │
│   │   └── prompts/               # AI Prompt 模板（YAML）
│   │       ├── v1/
│   │       │   ├── cleaner.yaml
│   │       │   ├── summarizer.yaml
│   │       │   ├── classifier.yaml
│   │       │   ├── tagger.yaml
│   │       │   ├── mindmap.yaml
│   │       │   ├── relation.yaml
│   │       │   ├── video.yaml
│   │       │   └── publication.yaml
│   │       └── loader.py          # Prompt 加载器
│   │
│   ├── tests/                     # 测试
│   │   ├── test_processor.py
│   │   ├── test_crawler.py
│   │   ├── test_api.py
│   │   ├── test_feedback.py
│   │   └── test_storage.py
│   │
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── web/                           # 前端（React + TypeScript）
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── ArticleDetail.tsx
│   │   │   ├── Graph.tsx          # P1
│   │   │   ├── Sources.tsx
│   │   │   ├── Upload.tsx
│   │   │   └── Publications.tsx   # P1
│   │   ├── components/
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── TagList.tsx
│   │   │   ├── CategoryTree.tsx
│   │   │   ├── MindmapView.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── FeedbackButtons.tsx # 👍👎
│   │   │   └── FileUploader.tsx
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── store/                 # Zustand 状态管理
│   │   └── types/
│   │
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.ts
│   └── vite.config.ts
│
├── data/                          # 运行时数据（.gitignore）
│   ├── articles/                  # Markdown 文章
│   │   └── {YYYY}/{MM}/
│   ├── uploads/                   # 用户上传的原始文件
│   ├── chroma/                    # ChromaDB 向量数据
│   ├── skill_memory/              # SKILL 用户画像缓存
│   └── hub.db                     # SQLite 主数据库
│
├── skills/
│   └── econ-master/
│       └── SKILL.md               # 经济大师 SKILL 定义
│
├── docs/
│   └── superpowers/specs/
│       └── 2026-04-20-finance-knowledge-hub-design_final.md
│
├── .env.example
├── .gitignore
├── Makefile                       # 统一命令入口
└── README.md
```

### 5.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件夹 | 全小写，单数 | `api/`、`core/` |
| Python 文件 | 全小写，蛇形 | `processor.py`、`storage.py` |
| React 页面/组件 | 大驼峰 | `Dashboard.tsx`、`ArticleCard.tsx` |
| API 路径 | 全小写，短横线 | `/api/articles`、`/api/search/semantic` |
| 数据库表 | 全小写，蛇形，复数 | `articles`、`knowledge_edges` |
| 环境变量 | 全大写，下划线 | `OPENAI_API_KEY` |

---

## 6. PRD — 产品需求

### 6.1 功能模块（严格分档）

**MVP — 最小可用版本（先做这些，没有就跑不通）**

| 模块 | 功能 | 说明 |
|------|------|------|
| 采集引擎 | Firecrawl 定时爬取 + 去重 | 对接 3-5 个财经源，URL+标题哈希去重 |
| AI 处理 | 清洗 + 摘要 + 分类 + 标签 | 四步流水线，每篇文章必经 |
| 分类体系 | 二级分类 + 标签 | 6 大领域各 4-6 个子类，标签承载细分 |
| 知识存储 | SQLite + Markdown + ChromaDB | 三份存储各司其职 |
| Web 前端 | 仪表盘 + 知识库 + 文章详情 + 上传 | 响应式布局，手机浏览器直接能用 |
| 搜索 | 全文搜索（FTS5） | 关键词搜索 |
| 数据源管理 | 增删改数据源 + 手动触发 | 管理采集来源 |
| 文件上传 | PDF/Word/TXT/EPUB 上传 | 手动导入文件 |
| SKILL | 经济大师基础版 | 能检索知识库、生成带引用回答 |

**P1 — 增强功能（MVP 跑通后立刻做）**

| 模块 | 功能 | 说明 |
|------|------|------|
| AI 处理 | 思维导图 + 关联分析 | 文章结构化 + 知识关联 |
| 知识图谱 | 力导向图可视化 | 文章关联网络展示 |
| 语义搜索 | 向量相似度搜索 | 用自然语言搜索 |
| 视频处理 | Whisper 转录 + 结构化 | 视频内容入库 |
| 文献管理 | 书籍/论文录入 + 章节管理 | 学术内容管理 |
| SKILL 进化 | 👍👎反馈 + 修正记录 + Few-shot 优化 | 让 AI 越用越懂你 |

**P2 — 体验优化（有余力再做）**

| 模块 | 功能 | 说明 |
|------|------|------|
| PWA 支持 | Service Worker + manifest | 可安装到桌面，离线读文章 |
| 批量导入 | 文件夹批量导入 | 一次性大量导入 |
| Prompt A/B 测试 | 同一任务两个 Prompt 版本对比 | 自动选优 |
| 用户记忆精细化 | 提问偏好、关注领域、回答风格 | 自动学习 |

**远期 — 商业化/规模化才做**

| 模块 | 功能 | 说明 |
|------|------|------|
| 云端迁移 | SQLite→PostgreSQL, 本地→S3 | 改配置切换，不改代码 |
| Capacitor App | 打包 iOS/Android | 复用 React 代码 |
| 多领域扩展 | 科技/法律等独立知识领域 | 新增领域 = 填表单 |
| 多用户支持 | 团队共享知识库 | JWT 认证 |

### 6.2 分类策略：二级分类 + 标签（终版决策）

**决策依据**：分类是互斥的（一篇文章只能在一个分类），层级越深 AI 越易分错、用户筛选越困惑。三级及以上的细分需求，用标签系统（多重、灵活）来承载。

```
【分类树】— 严格层级，互斥，用于左侧导航

宏观经济
├── 货币政策
├── 财政政策
├── 国际贸易
├── GDP/就业/通胀
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

学术文献（P1）
├── 经典著作
├── 工作论文
├── 期刊论文
└── 行业报告
```

```
【标签云】— 扁平化，多重，用于精细筛选

#降准 #降息 #LPR #MLF #公开市场操作  ← 货币政策的细分标签
#特斯拉 #比亚迪 #宁德时代 #电动车    ← 新能源行业的细分标签
#财报 #估值 #PE #PB #ROE #现金流      ← 公司研究的细分标签
#IPO #并购 #融资 #独角兽              ← 商业模型的细分标签
```

**用户使用场景**：
- "看所有货币政策文章" → 点分类：宏观经济/货币政策
- "只看降准相关的货币政策文章" → 先点分类，再筛选标签：#降准
- "看所有提到降准的文章（不管分类）" → 直接点标签：#降准

### 6.3 分类表设计（支持未来扩展，但 MVP 只用两层）

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES categories(id),  -- 自关联，预留 N 级扩展
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0,
    -- domain_id INTEGER REFERENCES knowledge_domains(id),  -- 远期：多领域预留
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**MVP 阶段**：只插入两级数据（parent_id = NULL 是一级，有 parent_id 是二级）。
**P1/P2 阶段**：仍只用两级，但表结构不限制。
**远期**：如需三级或跨领域，表结构已支持，只需加数据不加代码。

---


## 7. Prompt 设计（YAML 格式 + 版本管理）

### 7.1 Prompt 文件规范

每个 Prompt 是一个 `.yaml` 文件：

```yaml
version: 1                        # Prompt 版本号
name: xxx                         # 唯一名称
description: 一句话说明用途       # 人读的说明
model: gpt-4o-mini                # 默认使用的模型
inputs:                           # 声明输入参数
  - name: raw_content
    required: true
    description: 原始网页内容
system: |                         # System Prompt
  你是......
user: |                           # User Prompt 模板（{{变量名}} 占位）
  ......
```

> 改 Prompt 不需要改代码，不需要重启。有版本号，未来可 A/B 测试。

### 7.2 内容清洗

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
  你是一名专业的财经内容编辑。从原始网页内容中提取纯净的文章正文。
  
  规则：
  1. 只保留文章核心正文，保留段落结构
  2. 去除广告文案（如"点击关注"、"扫码入群"等）
  3. 去除作者个人介绍和版权声明
  4. 保留数据、图表的文字描述
  5. 输出纯文本，不含HTML标签
  6. 如果内容非财经/经济/商业/学术相关，返回 [IRRELEVANT]
user: |
  原始内容：
  {{raw_content}}
  
  请提取纯净正文：
```

### 7.3 智能摘要

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

### 7.4 自动分类（严格二级）

```yaml
# server/src/prompts/v1/classifier.yaml
version: 1
name: article_classifier
description: 将文章归入预定义二级分类体系
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
    description: 当前分类体系（从数据库/配置读取，不写死）
system: |
  你是一名财经内容分类专家。请将文章归入给定分类体系中最匹配的二级节点。
  
  规则：
  1. 必须选择【一级分类】和【二级分类】各一个
  2. 不允许自创分类，必须从给定的分类体系中选
  3. 如果文章同时涉及多个领域，选择最核心、占比最大的那个
  4. 二级分类是最终叶子节点，不需要更细的层级
  
  输出格式（严格JSON）：
  {
    "primary_category": "一级分类名称",
    "secondary_category": "二级分类名称",
    "confidence": 0.0-1.0,
    "reason": "分类理由（20字内）"
  }
user: |
  标题：{{title}}
  摘要：{{summary}}
  关键要点：{{key_points}}
  
  分类体系（只从以下列表中选择）：
  {{categories}}
  
  请分类：
```

> **关键约束**：Prompt 里明确告诉 AI "二级分类是最终叶子节点"，防止 AI 输出三级分类。

### 7.5 标签提取（承载细分需求）

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
  从财经文章中提取5-10个精准标签。标签要求：
  1. 包含关键实体（公司名、政策名、人物）
  2. 包含核心概念（如"量化宽松"、"IPO"、"ESG"）
  3. 标签简洁，2-6个字为佳
  4. 避免过于宽泛的词（如"经济"、"市场"）
  5. 【重要】如果文章涉及二级分类下的具体细分主题，用标签来体现
     例如：分类是"宏观经济/货币政策"，标签可以是"降准"、"LPR"、"MLF"
  
  输出格式：["标签1", "标签2", ...]
user: |
  标题：{{title}}
  摘要：{{summary}}
  实体：{{entities}}
  
  请提取标签：
```

### 7.6 思维导图

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

### 7.7 关联分析

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

### 7.8 视频内容结构化

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

### 7.9 文献/书籍解析

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

## 8. 数据库设计

### 8.1 迁移策略

```
改表流程：
1. 修改 server/src/db/models.py 中的 ORM 模型
2. 运行 make db-migrate msg="添加xxx字段" 自动生成迁移脚本
3. 运行 make db-upgrade 执行迁移
4. 迁移脚本永久保留在 migrations/versions/ 中
```

### 8.2 完整表结构

```sql
-- ============================================================
-- 分类体系（支持 N 级自关联，但 MVP 只用两级）
-- ============================================================

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 数据源配置
-- ============================================================

CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    driver TEXT NOT NULL DEFAULT 'firecrawl',
    config TEXT,
    schedule TEXT,
    is_active INTEGER DEFAULT 1,
    last_crawled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 文章核心表
-- ============================================================

CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    url TEXT UNIQUE,
    title TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,

    clean_content TEXT,
    summary TEXT,
    key_points TEXT,
    entities TEXT,
    sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')),
    importance TEXT CHECK(importance IN ('high', 'medium', 'low')),
    mindmap TEXT,

    -- 二级分类（外键关联 categories 表）
    primary_category_id INTEGER REFERENCES categories(id),
    secondary_category_id INTEGER REFERENCES categories(id),

    md_file_path TEXT,

    status TEXT DEFAULT 'pending' CHECK(status IN (
        'pending', 'crawled', 'cleaning', 'processing', 'completed', 'failed'
    )),
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 标签系统（承载三级及以上细分）
-- ============================================================

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- ============================================================
-- 知识图谱
-- ============================================================

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

-- ============================================================
-- 全文搜索
-- ============================================================

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
    segments TEXT,
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
    authors TEXT,
    publisher TEXT,
    isbn TEXT,
    doi TEXT,
    url TEXT,
    abstract TEXT,
    keywords TEXT,
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
    article_id INTEGER REFERENCES articles(id)
);

-- ============================================================
-- SKILL 进化（MVP 基础版，P1 完善）
-- ============================================================

CREATE TABLE skill_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL DEFAULT 'econ-master',
    query TEXT NOT NULL,
    response_summary TEXT,
    rating INTEGER CHECK(rating IN (-1, 0, 1)),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    field TEXT NOT NULL,
    original_value TEXT,
    corrected_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引（性能）
-- ============================================================

CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_primary_category ON articles(primary_category_id);
CREATE INDEX idx_articles_secondary_category ON articles(secondary_category_id);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_importance ON articles(importance);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_sources_is_active ON sources(is_active);
CREATE INDEX idx_skill_feedback_skill ON skill_feedback(skill_name);
CREATE INDEX idx_corrections_article ON corrections(article_id);
```

### 8.3 Markdown 文件格式

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
  - 政策意图
    - 支持实体经济
    - 稳定经济增长

## 正文

[清洗后的完整正文...]
```

---


## 9. API 设计

```yaml
# ── 采集 ────────────────────────────────
POST   /api/crawler/sources           # 新增数据源
GET    /api/crawler/sources           # 获取所有数据源
PUT    /api/crawler/sources/{id}      # 更新数据源
DELETE /api/crawler/sources/{id}      # 删除数据源
POST   /api/crawler/trigger/{id}      # 手动触发采集

# ── 文章 ────────────────────────────────
GET    /api/articles                  # 文章列表（分页 + 筛选）
GET    /api/articles/{id}             # 文章详情
DELETE /api/articles/{id}             # 删除文章
GET    /api/articles/{id}/related     # 关联文章
POST   /api/articles/{id}/correct     # 提交分类/标签修正

# ── 上传 ────────────────────────────────
POST   /api/upload                    # 上传文件
GET    /api/upload/tasks              # 上传任务列表
GET    /api/upload/tasks/{id}         # 上传任务状态

# ── 分类与标签 ──────────────────────────
GET    /api/categories                # 分类树（支持 ?parent_id= 查子级）
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

# ── 文献 ────────────────────────────────
GET    /api/publications              # 文献列表
POST   /api/publications              # 新增文献
GET    /api/publications/{id}         # 文献详情
GET    /api/publications/{id}/chapters # 文献章节列表

# ── SKILL ───────────────────────────────
POST   /api/skill/feedback            # 提交回答反馈（👍👎）
GET    /api/skill/memory              # 读取用户记忆/画像
PUT    /api/skill/memory              # 更新用户记忆
GET    /api/skill/examples            # 获取 Few-shot 样本

# ── 知识领域（远期预留）─────────────────
GET    /api/domains                   # 所有知识领域
POST   /api/domains                   # 新增知识领域
PUT    /api/domains/{id}              # 编辑知识领域
DELETE /api/domains/{id}              # 删除知识领域
GET    /api/domains/{id}/categories   # 某领域的分类树
```

---

## 10. 前端线框图设计

### 10.1 页面清单

| 页面 | 路径 | 文件 | 档位 | 说明 |
|------|------|------|------|------|
| 仪表盘 | `/` | `Dashboard.tsx` | MVP | 统计概览 |
| 知识库 | `/library` | `Library.tsx` | MVP | 文章列表 + 二级分类筛选 + 标签筛选 |
| 文章详情 | `/article/:id` | `ArticleDetail.tsx` | MVP | 原文/摘要/导图/关联 |
| 上传中心 | `/upload` | `Upload.tsx` | MVP | 文件上传 + 进度 |
| 数据源 | `/sources` | `Sources.tsx` | MVP | 采集源管理 |
| 知识图谱 | `/graph` | `Graph.tsx` | P1 | 可视化网络 |
| 文献库 | `/publications` | `Publications.tsx` | P1 | 书籍/论文列表 |

### 10.2 仪表盘（/）

```
+-------------------------------------------------------------+
|  FinanceIntel Hub                      [搜索] [设置] [刷新]  |
+-------------------------------------------------------------+
|  +----------+ +----------+ +----------+ +----------+        |
|  | 今日新增  | | 本周累计  | | 待处理   | | 数据源   |        |
|  |   23     | |   156    | |    5     | |    8     |        |
|  +----------+ +----------+ +----------+ +----------+        |
+-------------------------------------------------------------+
|  +----------------------+  +----------------------+         |
|  |   分类分布饼图        |  |   情感趋势折线图      |         |
|  |                      |  |                      |         |
|  |   [宏观经济] 35%     |  |   ^ positive         |         |
|  |   [金融市场] 28%     |  |   - neutral          |         |
|  |   [行业分析] 20%     |  |   v negative         |         |
|  |   ...                |  |                      |         |
|  +----------------------+  +----------------------+         |
+-------------------------------------------------------------+
|  最新入库                                                     |
|  +---------------------------------------------------------+|
|  | ! 央行宣布降准0.5个百分点      宏观经济/货币政策  10分钟前||
|  | ! 特斯拉Q1财报超预期            公司研究/财报解读  32分钟前||
|  | ! 新能源车企价格战加剧          行业分析/新能源    1小时前 ||
|  +---------------------------------------------------------+|
+-------------------------------------------------------------+
```

### 10.3 知识库（/library）— 核心页面

```
+-------------------------------------------------------------+
|  FinanceIntel Hub    [搜索文章、标签...]            [筛选v] |
+--------------+----------------------------------------------+
|              |  全部文章 (156)    [最新 v] [列表|卡片]      |
|  分类         |                                              |
|  > 宏观经济   |  +----------------------------------------+  |
|  |  > 货币   |  | 央行宣布降准0.5个百分点                 |  |
|  |  > 财政   |  | # 降准 # 央行 # 流动性  | 宏观经济/货币政策|  |
|  > 金融市场   |  | 央行决定于2026年4月25日下调金融机...     |  |
|  > 行业分析   |  | :) 正面  |  * 高  |  10分钟前           |  |
|  > 商业模型   |  +----------------------------------------+  |
|  > 公司研究   |  +----------------------------------------+  |
|  > 监管政策   |  | 特斯拉Q1财报超预期                      |  |
|              |  | # 特斯拉 # 财报 # 电动车 | 公司研究/财报解读|  |
|  热门标签     |  | 特斯拉发布2026年第一季度财报...          |  |
|  # 降准       |  | :) 正面  |  * 高  |  32分钟前           |  |
|  # 美联储     |  +----------------------------------------+  |
|  # 人工智能   |                                              |
|  # ...        |  < 1  2  3 ... 10 >                          |
+--------------+----------------------------------------------+
```

> 左侧分类树只展示两级（一级折叠/展开，二级可选）。热门标签在分类下方，点击标签直接筛选跨分类的内容。

### 10.4 文章详情（/article/:id）

```
+-------------------------------------------------------------+
|  <- 返回知识库     央行宣布降准0.5个百分点          [操作v]  |
+-------------------------------------------------------------+
|  > 宏观经济 > 货币政策    # 降准 # 央行 # 流动性 # LPR       |
|  新浪财经    张三    2026-04-20                             |
+-------------------------------------------------------------+
|  +-----------------------------------------------------+   |
|  |  [原文]  [AI摘要]  [思维导图]  [关联文章]            |   |
|  +-----------------------------------------------------+   |
|                                                             |
|  [AI摘要 Tab]                                               |
|                                                             |
|  +-----------------------------------------------------+   |
|  |  AI结构化摘要                                        |   |
|  |                                                     |   |
|  |  核心观点：央行降准0.5个百分点，释放长期资金约1万亿   |   |
|  |                                                     |   |
|  |  关键要点：                                          |   |
|  |  * 降准0.5个百分点，4月25日生效                       |   |
|  |  * 释放长期资金约1万亿元                              |   |
|  |  * 降低实体经济融资成本                               |   |
|  |  * 市场预期LPR跟随下调                                |   |
|  |                                                     |   |
|  |  涉及实体：中国人民银行、LPR、金融机构                |   |
|  |  情感倾向：:) 正面  |  重要程度：* 高                 |   |
|  +-----------------------------------------------------+   |
|                                                             |
|  [思维导图 Tab - markmap渲染]                                |
|                                                             |
|                    降准政策                                  |
|                  /    |    \                                |
|            政策内容  市场影响  政策意图                       |
|            /    \     |      /    \                         |
|      降准0.5%  释放1万亿 LPR下行 支持实体 稳定增长           |
|                                                             |
|  [关联文章 Tab]                                              |
|  +-----------------------------------------------------+   |
|  |  主题关联: 央行公开市场操作解读 (2026-04-15)          |   |
|  |  延续关联: 2026年货币政策展望 (2026-04-10)            |   |
|  |  因果关联: 银行股集体上涨分析 (2026-04-20)            |   |
|  +-----------------------------------------------------+   |
|                                                             |
|  [👍 有用] [👎 不准确]  ← SKILL 进化反馈（MVP 预留位置）      |
|                                                             |
+-------------------------------------------------------------+
```

### 10.5 上传中心（/upload）— MVP 新增

```
+-------------------------------------------------------------+
|  上传中心                                        [+ 批量导入]|
+-------------------------------------------------------------+
|                                                             |
|  +-----------------------------------------------------+   |
|  |                                                     |   |
|  |          📁 拖拽文件到此处 或 点击选择                |   |
|  |                                                     |   |
|  |     支持：PDF / Word / TXT / EPUB / 图片 / 视频      |   |
|  |                                                     |   |
|  +-----------------------------------------------------+   |
|                                                             |
|  处理队列                                                    |
|  +-----------------------------------------------------+   |
|  | 文件名              类型    大小      状态             |   |
|  | -----------------  ------  --------  ----------       |   |
|  | 货币政策2026.pdf    PDF    2.3MB    [====>    ] 处理中 |   |
|  | 特斯拉研报.docx     Word   1.1MB    [========] 已完成  |   |
|  | 财经早餐.mp4        视频   156MB    [==>      ] 转录中  |   |
|  +-----------------------------------------------------+   |
|                                                             |
+-------------------------------------------------------------+
```

### 10.6 知识图谱（/graph）— P1

```
+-------------------------------------------------------------+
|  知识图谱                                        [力导图|环形]|
+-------------------------------------------------------------+
|                                                             |
|                    [央行降准]                                |
|                       |                                     |
|         +-------------+-------------+                       |
|         |                           |                       |
|    [货币政策]---[LPR下调]---[银行股]  [流动性]               |
|         |                           |                       |
|    [经济数据]                    [实体经济]                  |
|                                                             |
|  +-------------------------------------------------------+  |
|  | 选中：央行降准                                           |  |
|  | 分类：宏观经济/货币政策  |  标签：降准 央行 流动性        |  |
|  | [查看原文]  [查看关联]                                   |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

### 10.7 数据源管理（/sources）

```
+-------------------------------------------------------------+
|  数据源管理                                    [+ 新增数据源]|
+-------------------------------------------------------------+
|  +-------------------------------------------------------+  |
|  |  新浪财经                    [编辑] [删除] [立即采集]   |  |
|  |  https://finance.sina.com.cn  firecrawl  每2小时       |  |
|  |  上次采集：5分钟前  状态：正常  今日新增：12            |  |
|  +-------------------------------------------------------+  |
|  |  36氪                        [编辑] [删除] [立即采集]   |  |
|  |  https://36kr.com            RSS      每小时           |  |
|  |  上次采集：12分钟前 状态：正常  今日新增：8             |  |
|  +-------------------------------------------------------+  |
|  |  华尔街见闻                   [编辑] [删除] [立即采集]  |  |
|  |  https://wallstreetcn.com    firecrawl  每2小时        |  |
|  |  上次采集：1小时前  状态：正常  今日新增：3             |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

### 10.8 手机端适配（MVP 就做响应式）

```
电脑端：左右两栏                    手机端：单栏堆叠
+--------------+--------------+    +------------------+
| 分类          | 文章列表      |    | [搜索] [筛选▼]   |
| 树           |              |    +------------------+
|              | 文章1         |    | 文章1             |
| 热门         | 文章2         | -> | 文章2             |
| 标签         | 文章3         |    | 文章3             |
|              |              |    | ...               |
+--------------+--------------+    +------------------+
                                    分类/标签在顶部筛选抽屉
```

> TailwindCSS 的响应式类（`lg:flex-row flex-col`）搞定，MVP 阶段手机浏览器就能正常使用。

---

## 11. Firecrawl 采集方案

### 11.1 双驱动架构

```
采集引擎 (core/crawler.py)
│
├── FirecrawlDriver（主力，80% 来源）
│   ├── 输入：URL 或站点地图
│   ├── 输出：干净 Markdown + 标题/作者/时间
│   └── 适用：新闻站、博客、资讯页面
│
└── CustomDriver（兜底，20% 特殊源）
    ├── RSSParser（RSS/Atom 源）
    ├── APIClient（有开放 API 的平台）
    └── RawScraper（其他特殊情况）
```

### 11.2 数据源配置

```json
{
  "name": "新浪财经-宏观",
  "driver": "firecrawl",
  "config": {
    "url": "https://finance.sina.com.cn/china/",
    "limit": 20,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  },
  "schedule": "0 */2 * * *"
}
```

### 11.3 成本控制

| Firecrawl 方案 | 费用 | credits/月 | 用途 |
|---|---|---|---|
| Free | 免费 | 500 | 开发测试 |
| Pro | $19/月 | 5,000 | 个人日常使用 |
| Scale | $249/月 | 50,000 | 团队/高频 |

策略：设置每日 credit 上限，Firecrawl 处理标准网页，RSS/API 处理免费源。

---

## 12. 核心流水线

### 12.1 文章处理流水线

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

    # 3. AI 处理（摘要 + 分类 + 标签 并行）
    await db.update_status(article.id, "processing")
    summary, category, tags = await asyncio.gather(
        ai.run_prompt("summarizer", clean_content=clean),
        ai.run_prompt("classifier", title=..., summary=..., key_points=..., categories=...),
        ai.run_prompt("tagger", title=..., summary=..., entities=...),
    )

    # 4. 思维导图（P1）
    mindmap = await ai.run_prompt("mindmap", title=..., clean_content=clean)

    # 5. Embedding → ChromaDB
    await vector_store.add(article.id, clean)

    # 6. 关联分析（P1）
    relations = await ai.run_prompt("relation", ...)

    # 7. 写入数据库 + Markdown 文件
    await db.save_full_article(article.id, clean, summary, category, tags, mindmap)
    await save_markdown_file(article.id, ...)
    await db.save_relations(article.id, relations)

    await db.update_status(article.id, "completed")
    return article.id
```

### 12.2 状态机

```
pending → crawled → cleaning → processing → completed
                                    ↘
                                   failed（任何步骤失败跳转）
```

---


## 13. "经济大师" SKILL 设计

### 13.1 SKILL.md（完整版）

```markdown
---
name: econ-master
version: 1
description: 基于本地财经知识库的经济分析助手，支持持续进化
api_base: http://localhost:8000/api
---

# 经济大师模式

## 身份设定

你是 FinanceIntel Hub 首席经济分析师。你可以访问用户的本地财经知识库，
知识库涵盖：宏观经济、金融市场、行业分析、商业模型、公司研究、监管政策、经典著作、学术论文。

## 核心能力

1. **知识库检索**：回答任何问题前，先检索本地知识库获取相关素材
2. **多源融合**：整合网络热点、经典理论、学术论文给出综合判断
3. **证据引用**：每个观点必须标注来源（文章标题 + 日期 + 知识库ID）
4. **结构化输出**：复杂问题使用思维导图式层级结构呈现
5. **持续进化**：根据用户反馈（👍👎、修正记录）不断优化回答质量

## 工作流

### 步骤1：加载记忆（P1 完善）
读取用户画像和最近对话上下文，注入回答偏好。

### 步骤2：问题解析
分析用户问题的核心维度：
- 时间范围：历史回顾 / 当前状况 / 未来预测
- 分析深度：概念解释 / 现象分析 / 策略建议
- 涉及领域：宏观 / 市场 / 行业 / 公司 / 政策

### 步骤3：知识库检索
```
GET {api_base}/search/semantic?q={用户问题}&limit=10   ← 语义搜索（主要）
GET {api_base}/search?q={关键词}&limit=5               ← 全文搜索（补充）
GET {api_base}/graph/subgraph?article_id={id}&depth=2  ← 知识图谱扩展
GET {api_base}/skill/examples                          ← 获取 Few-shot 样本（P1）
```

检索优先级：
1. 语义搜索 → 找最相关的 5-10 篇文章
2. 全文搜索 → 补充关键词匹配
3. 知识图谱 → 找关联文章扩展视角
4. 经典文献 → 寻找理论支撑

### 步骤4：证据整合
对检索结果进行加权排序：

| 来源类型 | 权重 | 说明 |
|----------|------|------|
| 高重要性+近期文章 | 1.0 | 核心论据 |
| 经典著作/论文 | 0.9 | 理论支撑 |
| 普通文章 | 0.7 | 补充视角 |
| 关联文章 | 0.5 | 背景信息 |

### 步骤5：生成回答

回答结构模板：

```
## 核心判断

[一句话给出核心观点]

## 分析框架

[思维导图式层级结构]
- 维度1
  - 论点1（引用：文章标题 2026-04-20 #ID）
  - 论点2（引用：论文标题 作者 年份）
- 维度2
  ...

## 数据与事实

[列出关键数据，每项标注来源]
- 数据1：数值（来源）
- 数据2：数值（来源）

## 风险提示

[基于知识库的历史类似案例给出风险警示]

## 延伸阅读

[推荐知识库中3-5篇相关文章，附链接/ID]
```

## 回答风格

- **专业严谨**：使用规范经济学术语，避免口语化
- **数据驱动**：优先用数据说话，而非主观判断
- **历史视角**：结合历史案例和周期规律
- **批判思维**：呈现多方观点，指出争议点
- **可操作**：给出明确的结论和投资/决策建议

## 约束

1. **禁止编造**：不能引用知识库中不存在的文章或数据
2. **时效标注**：明确区分"最新数据"和"历史数据"
3. **不确定性**：预测性观点必须标注置信度（高/中/低）
4. **冲突处理**：当知识库中存在矛盾观点时，必须呈现双方论据
5. **用户修正**：用户修正过的分类/标签，后续遵循用户的判断

## 特殊指令

- `/deep` — 深度分析模式 → 检索20+篇文章，生成3000字以上报告
- `/compare` — 对比分析模式 → 检索多个对象的资料进行对比
- `/timeline` — 时间线模式 → 按时间顺序梳理事件演进
- `/paper` — 学术模式 → 优先引用论文和经典著作，使用学术规范
- `/forget` — 清除用户记忆，重新开始（P1）
- `/profile` — 查看当前用户画像（P1）

---
💡 这个回答对你有帮助吗？ [👍 有用] [👎 不准确] [✏️ 补充]
```

### 13.2 SKILL 进化机制（MVP 基础版 → P1 完善版）

**MVP 阶段（基础反馈收集）**：
- 文章详情页底部显示 👍👎 按钮
- 用户点击后，记录到 `skill_feedback` 表
- 数据积累，但暂不自动优化 Prompt

**P1 阶段（闭环进化）**：

```
用户反馈收集
    │
    ├──→ 👍👎 评分 → 存入 skill_feedback 表
    ├──→ ✏️ 修正分类/标签 → 存入 corrections 表
    └──→ 📝 补充评论 → 存入 skill_feedback.comment
    │
    ▼
Few-shot 样本生成（定时任务，每日一次）
    │
    ├──→ 从 corrections 表提取修正记录
    ├──→ 按 field（分类/标签）聚类
    └──→ 生成 Few-shot 样本 JSON
    │
    ▼
Prompt 自动优化
    │
    ├──→ 加载 Prompt YAML 模板
    ├──→ 在 system 尾部注入 Few-shot 样本
    └──→ 保存为新版本 prompts/v2/classifier.yaml
    │
    ▼
下次同类任务使用优化后的 Prompt
```

**P2 阶段（精细化）**：
- 用户记忆层：`skill_memory` 表记录关注领域、回答风格偏好
- Prompt A/B 测试：同一任务跑两个 Prompt 版本，对比好评率

**进化效果预期**：

| 反馈数量 | 效果 |
|----------|------|
| 10 条 | 开始积累修正样本 |
| 50 条 | Few-shot 注入后，分类准确率明显提升 |
| 100 条 | AI 开始适配用户偏好，回答更有针对性 |
| 300 条 | 像一个懂你的私人分析师 |

---

## 14. 多端策略

### 14.1 三步走（明确档位）

| 步骤 | 档位 | 内容 | 技术 |
|------|------|------|------|
| **第一步** | MVP | 响应式 Web | TailwindCSS 媒体查询 |
| **第二步** | P2 | PWA（可安装 + 离线缓存） | Service Worker + manifest.json |
| **第三步** | 远期 | Capacitor 打包 iOS/Android | 复用 React 代码 |

### 14.2 为什么 MVP 只做响应式？

| 方案 | 开发成本 | 用户体验 | 决策 |
|------|----------|----------|------|
| 响应式 Web | 几乎为零 | 够用（80分） | ✅ MVP 做 |
| PWA | 2-3 天 | 很好（90分） | 🟡 P2 做 |
| Capacitor 打包 | 1-2 周 | 优秀（95分） | 🔵 远期做 |
| React Native 原生 | 4-8 周 | 最好（100分） | ❌ 不做 |

### 14.3 MVP 就做的准备

- 前端用 TailwindCSS — 天然支持响应式
- API 设计是 RESTful JSON — 任何端都能调用
- 数据逻辑在后端 — 前端只是"展示层"

---

## 15. 云迁移路径（只预留，不实现）

### 15.1 三层抽象层设计

```python
# server/src/core/storage.py —— 存储后端抽象

class StorageBackend:
    """存储后端抽象：本地和云端共用同一个接口"""
    def save(self, path: str, content: bytes): ...
    def load(self, path: str) -> bytes: ...
    def delete(self, path: str): ...

class LocalStorage(StorageBackend):
    """本地文件系统 —— MVP 只实现这个"""
    ...

class S3Storage(StorageBackend):
    """AWS S3 / 阿里云 OSS —— 远期实现，预留接口"""
    ...
```

### 15.2 数据库切换

```python
# server/src/db/engine.py

from config import settings

# SQLAlchemy 通过 URL 格式自动识别数据库类型
engine = create_engine(settings.DATABASE_URL)
# sqlite:///...  → 用 SQLite（MVP）
# postgresql://... → 用 PostgreSQL（远期）
# 代码完全一样，一行不用改
```

### 15.3 配置预留

```bash
# .env.example —— 本地配置（MVP 启用）
DATABASE_URL=sqlite:///./data/hub.db
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/chroma
STORAGE_BACKEND=local
STORAGE_PATH=./data

# 以下配置预留，暂不启用
# DATABASE_URL=postgresql://...
# VECTOR_DB=pinecone
# STORAGE_BACKEND=s3
```

> **关键原则**：代码里实现抽象接口，但 MVP 只接本地实现。未来迁移时，改 `.env` 配置即可，不改代码。

---

## 16. 升级路线图

### 阶段一：MVP（第 1-3 周）

**目标**：跑通核心流程——采集 → AI 处理 → 存储 → 展示 → 上传 → SKILL 基础

```
做什么：
✅ 后端：FastAPI + SQLite + ChromaDB
✅ 采集：Firecrawl 对接 3-5 个财经源
✅ AI：清洗 + 摘要 + 分类 + 标签（四步流水线）
✅ 分类：二级分类 + 标签体系
✅ 前端：仪表盘 + 知识库 + 文章详情 + 上传中心 + 数据源管理
✅ 搜索：全文搜索（FTS5）
✅ 上传：PDF / Word / TXT / EPUB
✅ SKILL：经济大师基础版（能检索、能回答、能收集反馈）
✅ 响应式布局：手机浏览器能用

不做什么：
❌ 知识图谱可视化
❌ 语义搜索
❌ 视频处理
❌ 文献管理
❌ SKILL 自动进化（只收集反馈，不自动优化）
❌ PWA / App
❌ 云端
```

### 阶段二：增强（第 3-5 周）

**目标**：知识关联 + 视频 + 文献 + 智能搜索 + SKILL 进化

```
新增：
✅ 思维导图生成 + markmap 渲染
✅ 关联分析 + 知识图谱可视化（D3.js）
✅ 语义搜索（ChromaDB 向量检索）
✅ 视频处理（Whisper 转录 + 结构化）
✅ 文献管理（书籍 / 论文 / 章节）
✅ SKILL 进化闭环（Few-shot 自动注入）
✅ 👍👎 反馈 + 修正记录前端交互

架构不变，只加功能。
```

### 阶段三：智能化（第 5-8 周）

**目标**：体验打磨 + 用户记忆 + PWA

```
新增：
✅ PWA 支持（离线缓存 + 桌面安装）
✅ 用户记忆层（关注领域、回答风格偏好）
✅ Prompt A/B 测试
✅ 批量导入
✅ 推送通知（"今日有 5 篇重要文章"）

可选架构升级（按需）：
🔄 SQLite → PostgreSQL（数据量大了再切）
🔄 单进程 → 后台任务队列（处理量大了再切）
```

### 阶段四：云端 + 多端（第 8-12 周）

**目标**：随时随地可用，数据安全上云

```
新增：
✅ 存储抽象层接入 S3/OSS
✅ 数据库迁移到 PostgreSQL
✅ 向量数据库迁移到 Pinecone（按需）
✅ Capacitor 打包 iOS/Android App
✅ 新增第二个知识领域验证扩展机制
```

### 远期（第 12 周+）

| 方向 | 触发条件 | 做什么 |
|------|----------|--------|
| 多用户 | 需要分享给团队 | 加 `users` 表 + JWT 认证 |
| 多领域 SKILL | 知识库扩展到 3+ 领域 | 新增 `tech-analyst` 等 SKILL |
| 自动化报告 | 日/周报需求 | 定时 AI 生成综合分析报告 |
| 插件市场 | 数据源类型太多 | `core/crawler.py` 改为插件注册机制 |

---

## 17. 技术风险与规避

| 风险 | 规避措施 |
|------|----------|
| 爬虫被封 IP | 控制频率、Firecrawl 自带反封、遵守 robots.txt |
| AI API 费用过高 | gpt-4o-mini 跑清洗/分类/标签；gpt-4o 只做摘要/关联；设每日上限 |
| 文章去重不准 | URL 精确匹配 + 标题相似度双重校验 |
| AI 分类不准 | 用户修正 → Few-shot 样本积累 → Prompt 自动优化（P1） |
| 向量数据库膨胀 | 定期归档，按月分 Collection |
| 数据库改表 | Alembic 迁移，自动生成升级脚本 |
| 云迁移数据丢失 | 迁移前自动备份；存储抽象层让切换无需改代码（预留） |
| SKILL 记忆偏差 | `/forget` 命令可清除记忆；记忆有上限（最近 100 条交互） |
| 手机端体验差 | MVP 就用 TailwindCSS 响应式；PWA 提供类 App 体验 |
| 三级分类需求 | 用标签系统承载，分类只到二级 |

---

## 18. 测试策略

```
测试什么：                      不测什么：
✅ AI Prompt 输出格式是否正确    ❌ 第三方库内部逻辑
✅ 流水线状态流转是否正确        ❌ 前端 UI 样式
✅ 去重逻辑是否有效
✅ API 入参校验是否正确
✅ 数据库迁移是否能跑通
✅ 存储抽象层接口一致性（预留）
✅ 反馈写入和 Few-shot 样本生成
```

目录：`server/tests/`，使用 `pytest`，运行 `make test`。

---

## 19. 配置与启动

### 19.1 环境变量 (.env.example)

```bash
# ── AI 服务 ──────────────────────
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL_PRIMARY=gpt-4o
OPENAI_MODEL_FAST=gpt-4o-mini

# ── 采集服务 ──────────────────────
FIRECRAWL_API_KEY=fc-xxx

# ── 数据存储（本地模式）───────────
DATA_DIR=./data
DATABASE_URL=sqlite:///./data/hub.db
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/chroma
STORAGE_BACKEND=local
STORAGE_PATH=./data

# ── 服务端口 ──────────────────────
SERVER_PORT=8000

# ── SKILL 配置 ────────────────────
SKILL_FEEDBACK_ENABLED=true
SKILL_EVOLUTION_ENABLED=false      # MVP 只收集，P1 开启自动优化
```

### 19.2 Makefile

```makefile
# ── 开发 ─────────────────────────
dev:
	cd server && uvicorn src.main:app --reload --port 8000 &
	cd web && npm run dev

# ── 数据库 ───────────────────────
db-migrate:
	cd server && alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd server && alembic upgrade head

db-reset:
	rm -f data/hub.db && cd server && alembic upgrade head

# ── 安装 ─────────────────────────
install:
	cd server && pip install -r requirements.txt
	cd web && npm install

# ── 测试 ─────────────────────────
test:
	cd server && pytest tests/ -v

# ── 生产 ─────────────────────────
build:
	cd web && npm run build

prod:
	cd server && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 19.3 启动方式

```bash
# 第一次：
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 和 FIRECRAWL_API_KEY
make install
make db-upgrade
make dev

# 之后每次：
make dev
# 打开浏览器访问 http://localhost:5173
```

---

## 20. 文档整合说明

本终版设计文档整合了三份输入的最优部分：

| 来源 | 被吸收的内容 | 被调整/舍弃的内容 |
|------|-------------|------------------|
| **v1.1（Kimi）** | SKILL.md 完整工作流和约束；视频/文献/上传模块设计；前端线框图 | 目录结构深度偏深（routers/services）→ 改为 api/core 扁平化 |
| **v2.0（Claude）** | 大白话开场；YAML Prompt 规范；Alembic 迁移；状态机；Makefile；目录命名规范 | 分类表设计未明确二级策略 → 补充"二级分类+标签"决策 |
| **v2.1（Claude）** | 响应式 Web 预留；存储抽象层接口；SKILL 进化概念 | 过度工程部分：A/B 测试、用户记忆精细化、四张反馈表、多领域扩展、S3 具体实现 → 全部降级为"预留接口，MVP 不实现" |

**核心设计哲学**：
> MVP 阶段代码只实现本地、Web端、二级分类、基础 SKILL。但每个功能的接口和抽象层都预留好扩展点，确保未来升级时"只改配置，不改代码"。

---

*FinanceIntel Hub 设计文档（终版）完成。等待开发计划（writing-plans）。*
