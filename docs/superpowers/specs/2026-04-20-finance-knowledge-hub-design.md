# FinanceIntel Hub — 财经智识库系统设计文档

> 版本：v1.0  
> 日期：2026-04-20  
> 状态：待审批

---

## 1. 三种技术方案对比

| 维度 | 方案A：轻量级单体（推荐） | 方案B：事件驱动队列 | 方案C：极简静态 |
|------|------------------------|-------------------|----------------|
| **架构** | FastAPI + React + SQLite | FastAPI + Celery + Redis + React | Python脚本 + 静态HTML |
| **爬虫调度** | APScheduler内置定时 | Celery Beat分布式定时 | cron定时执行 |
| **AI处理** | 同步API调用 | 异步队列消费 | 顺序执行 |
| **存储** | SQLite + 本地MD + Chroma | PostgreSQL + 本地MD + Chroma | JSON文件 + MD |
| **前端** | React SPA（Vite） | React SPA（Vite） | 无交互静态页 |
| **部署** | 单命令启动 | 多服务编排 | 直接运行 |
| **复杂度** | ⭐⭐☆ | ⭐⭐⭐⭐ | ⭐☆☆ |
| **扩展性** | 中 | 高 | 低 |
| **开发周期** | 2-3周 | 4-6周 | 1周（功能弱） |

**推荐方案A**。理由：满足所有需求且无过度工程；单体架构足够支撑个人/小团队使用；SQLite+Chroma零配置；单命令启动降低维护成本。

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层 (React 18 + Vite)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 仪表盘    │ │ 知识库    │ │ 文章详情  │ │ 知识图谱  │ │ 系统设置  │      │
│  │ Dashboard│ │ Library  │ │ Article  │ │ Graph    │ │ Settings │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼────────────┼────────────┘
        │            │            │            │            │
        └────────────┴────────────┴─────┬──────┴────────────┴────────────┘
                                        │ REST API
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            后端层 (FastAPI)                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                         API Router                                │  │
│  │  /api/crawler  /api/articles  /api/graph  /api/search  /api/admin │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │ 采集引擎    │ │ AI处理引擎  │ │ 搜索引擎    │ │ 管理模块    │          │
│  │ Crawler    │ │ Processor  │ │ Search     │ │ Admin      │          │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘          │
└────────┼──────────────┼──────────────┼──────────────┼──────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            数据层                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ SQLite       │  │ ChromaDB     │  │ 本地文件系统  │  │ APScheduler │ │
│  │ 结构化数据    │  │ 向量数据库    │  │ Markdown原文 │  │ 定时任务     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         外部服务层                                       │
│  ┌─────────────────┐  ┌─────────────────────────────────────────────┐  │
│  │ OpenAI API      │  │ 财经网站源：新浪财经/36氪/华尔街见闻/财新   │  │
│  │ GPT-4o / o3-mini│  │ RSS / API / 网页原始数据采集                 │  │
│  └─────────────────┘  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
[定时触发] → [爬虫采集] → [原始HTML] → [AI内容清洗] → [结构化数据]
                                                        ↓
[用户查询] ← [RAG检索] ← [向量数据库] ← [Embedding] ← [摘要+标签+分类]
                                                        ↓
                                              [Markdown存储] → [知识图谱构建]
                                                        ↓
                                              [前端展示: 文章/导图/关联]
```

---

## 3. PRD — 产品需求文档

### 3.1 功能模块

| 模块 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| **采集引擎** | 定时爬取热点 | P0 | 支持多源配置，可增删改数据源 |
| | 去重检测 | P0 | 基于URL+标题哈希去重 |
| **AI处理** | 内容清洗 | P0 | 去除广告/导航/无关内容，提取正文 |
| | 智能摘要 | P0 | 生成3-5条 bullet point 摘要 |
| | 自动分类 | P0 | 归入预定义分类体系 |
| | 标签提取 | P0 | 提取5-10个关键词标签 |
| | 思维导图 | P1 | 生成文章结构导图（层级大纲） |
| | 关联分析 | P1 | 与已有文章建立知识关联 |
| **视频处理** | 音频提取 | P1 | 从视频文件提取音频轨道 |
| | 语音转录 | P1 | Whisper转录为文字 |
| | 内容分段 | P1 | 按主题/时间戳分段 |
| **主动上传** | 文件上传 | P0 | 支持PDF/Word/图片/视频/EPUB/TXT |
| | 批量导入 | P1 | 文件夹批量导入 |
| | 书籍/文献管理 | P1 | 经典书籍、论文、文献结构化入库 |
| **文献引擎** | 书籍录入 | P1 | 书名/作者/ISBN/章节结构 |
| | 论文解析 | P1 | 解析arXiv/PDF论文，提取摘要/方法/结论 |
| | 文献引用网络 | P2 | 论文间引用关系图谱 |
| **知识存储** | Markdown持久化 | P0 | 每篇文章独立MD文件，含YAML Frontmatter |
| | 元数据库 | P0 | SQLite存储文章元数据、分类、标签、关联 |
| | 向量索引 | P0 | ChromaDB存储Embedding，支持语义检索 |
| **Web前端** | 仪表盘 | P0 | 今日新增、热点分布、采集统计 |
| | 知识库列表 | P0 | 文章列表、分类筛选、标签筛选、搜索 |
| | 文章详情 | P0 | 原文/摘要切换、思维导图、关联推荐 |
| | 知识图谱 | P1 | 力导向图展示文章关联网络 |
| | 数据源管理 | P0 | 增删改爬虫源、手动触发、频率设置 |
| | 上传中心 | P0 | 文件上传、处理进度、批量管理 |
| | 文献库 | P1 | 书籍列表、论文库、章节浏览 |
| **搜索** | 全文检索 | P0 | 基于SQLite FTS |
| | 语义搜索 | P1 | 基于向量相似度 |

### 3.2 预定义分类体系（经济学/金融/商业）

```
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
```

---

## 4. Prompt设计

### 4.1 内容清洗 Prompt

```yaml
name: content_cleaner
system: |
  你是一名专业的财经内容编辑。你的任务是从原始网页内容中提取纯净的文章正文，
  去除所有广告、导航栏、页脚、相关推荐、作者介绍等无关内容。
  
  规则：
  1. 只保留文章核心正文，保留段落结构
  2. 去除明显的广告文案（如"点击关注"、"扫码入群"等）
  3. 去除作者个人介绍和版权信息
  4. 保留数据、图表的文字描述
  5. 输出纯文本，不要任何HTML标签
  6. 如果内容非财经/经济/商业相关，返回 [IRRELEVANT]
  
user_template: |
  原始内容：
  {{{raw_content}}}
  
  请提取纯净正文：
```

### 4.2 智能摘要 Prompt

```yaml
name: article_summarizer
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
  
user_template: |
  文章内容：
  {{{clean_content}}}
  
  请生成结构化摘要：
```

### 4.3 自动分类 Prompt

```yaml
name: article_classifier
system: |
  你是一名财经内容分类专家。请将文章归入以下分类体系中最匹配的节点：
  
  分类体系：
  - 宏观经济（货币政策、财政政策、国际贸易、GDP/就业/通胀、全球经济）
  - 金融市场（股票市场、债券市场、外汇市场、大宗商品、加密货币、市场策略）
  - 行业分析（科技互联网、房地产、制造业、医疗健康、新能源、消费零售）
  - 商业模型（商业模式创新、企业战略、投资并购、创业融资、公司治理）
  - 公司研究（财报解读、竞争分析、管理层动态、估值分析）
  - 监管政策（金融监管、行业监管、反垄断、数据合规）
  
  输出格式（严格JSON）：
  {
    "primary_category": "一级分类",
    "secondary_category": "二级分类",
    "confidence": 0.0-1.0,
    "reason": "分类理由（20字内）"
  }
  
user_template: |
  标题：{{title}}
  摘要：{{summary}}
  关键要点：{{key_points}}
  
  请分类：
```

### 4.4 标签提取 Prompt

```yaml
name: tag_extractor
system: |
  从财经文章中提取5-10个精准标签。标签要求：
  1. 包含关键实体（公司名、政策名、人物）
  2. 包含核心概念（如"量化宽松"、"IPO"、"ESG"）
  3. 标签简洁，2-6个字为佳
  4. 避免过于宽泛的词（如"经济"、"市场"）
  
  输出格式：["标签1", "标签2", ...]
  
user_template: |
  标题：{{title}}
  摘要：{{summary}}
  实体：{{entities}}
  
  请提取标签：
```

### 4.5 思维导图 Prompt

```yaml
name: mindmap_generator
system: |
  将财经文章转化为层级化的思维导图结构。
  
  输出格式（严格Markdown列表，最多3层）：
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
  
user_template: |
  标题：{{title}}
  内容：
  {{{clean_content}}}
  
  请生成思维导图结构：
```

### 4.6 视频内容结构化 Prompt

```yaml
name: video_structurer
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
  
user_template: |
  视频转录内容（含时间戳）：
  {{{transcript_segments}}}
  
  请结构化：
```

### 4.7 文献/书籍解析 Prompt

```yaml
name: publication_parser
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
  
user_template: |
  文献内容：
  {{{content}}}
  
  文献类型：{{pub_type}}  <!-- book_chapter | paper | report -->
  标题：{{title}}
  作者：{{authors}}
  
  请深度解析：
```

### 4.8 关联分析 Prompt

```yaml
name: relation_analyzer
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
  
  如果无强关联，related_articles可为空。
  
user_template: |
  当前文章：
  标题：{{current_title}}
  摘要：{{current_summary}}
  分类：{{current_category}}
  标签：{{current_tags}}
  
  已有文章列表（最多提供20篇最相关）：
  {{existing_articles}}
  
  请分析关联：
```

---

## 5. 数据库设计

### 5.1 SQLite 结构化数据

```sql
-- 数据源配置
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- 源名称：如"新浪财经"
    url TEXT NOT NULL,               -- 源URL
    source_type TEXT NOT NULL,       -- rss | api | static
    crawl_config TEXT,               -- JSON：选择器、频率等
    is_active BOOLEAN DEFAULT 1,
    last_crawled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文章主表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    url TEXT UNIQUE NOT NULL,        -- 原文URL
    title TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,
    
    -- AI处理结果
    clean_content TEXT,              -- 清洗后的正文
    summary TEXT,                    -- 概述
    key_points TEXT,                 -- JSON数组
    entities TEXT,                   -- JSON数组
    sentiment TEXT,                  -- positive | neutral | negative
    importance TEXT,                 -- high | medium | low
    
    -- 分类
    primary_category TEXT,
    secondary_category TEXT,
    
    -- 存储
    md_file_path TEXT,               -- 本地MD文件路径
    
    -- 状态
    status TEXT DEFAULT 'pending',   -- pending | processing | completed | failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,                   -- 实体|概念|政策
    usage_count INTEGER DEFAULT 0
);

-- 文章标签关联
CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- 知识图谱关系
CREATE TABLE knowledge_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    target_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,     -- 主题关联|因果关联|对比关联|延续关联
    strength REAL,                   -- 关联强度 0-1
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_article_id, target_article_id, relation_type)
);

-- 全文搜索虚拟表
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, clean_content, 
    content='articles',
    content_rowid='id'
);

-- 上传任务表（处理队列）
CREATE TABLE upload_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,         -- pdf | docx | image | video | epub | txt
    file_size INTEGER,
    status TEXT DEFAULT 'pending',   -- pending | processing | completed | failed
    error_message TEXT,
    article_id INTEGER REFERENCES articles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 视频转录记录
CREATE TABLE video_transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_path TEXT NOT NULL,
    audio_path TEXT,
    transcript_text TEXT,            -- 完整转录文本
    segments TEXT,                   -- JSON: [{start, end, text}, ...]
    language TEXT DEFAULT 'zh',
    model_used TEXT DEFAULT 'whisper-1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 书籍/文献表
CREATE TABLE publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pub_type TEXT NOT NULL,          -- book | paper | report
    title TEXT NOT NULL,
    authors TEXT,                    -- JSON数组
    publisher TEXT,
    isbn TEXT,
    doi TEXT,
    url TEXT,
    abstract TEXT,
    keywords TEXT,                   -- JSON数组
    publication_date TEXT,
    file_path TEXT,                  -- 本地PDF/EPUB路径
    source TEXT,                     -- 上传 | arxiv | jstor | 知网
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 书籍章节（用于经典著作的结构化管理）
CREATE TABLE publication_chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_id INTEGER REFERENCES publications(id) ON DELETE CASCADE,
    chapter_number INTEGER,
    title TEXT NOT NULL,
    summary TEXT,                    -- AI生成的章节摘要
    start_page INTEGER,
    end_page INTEGER,
    content_text TEXT,               -- 提取的章节文本
    md_file_path TEXT                -- 章节独立MD文件
);
```

### 5.2 Markdown 文件格式

每篇文章存储为独立 `.md` 文件，路径：`storage/articles/{YYYY}/{MM}/{article_id}.md`

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
- 市场普遍预期此次降准后LPR将跟随下调

## 正文

[清洗后的完整正文...]

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
```

---

## 6. API 设计

```yaml
# 采集
POST   /api/crawler/sources           # 新增数据源
GET    /api/crawler/sources           # 获取所有数据源
PUT    /api/crawler/sources/{id}      # 更新数据源
DELETE /api/crawler/sources/{id}      # 删除数据源
POST   /api/crawler/trigger/{id}      # 手动触发采集

# 文章
GET    /api/articles                  # 文章列表（支持筛选、分页）
GET    /api/articles/{id}             # 文章详情
DELETE /api/articles/{id}             # 删除文章
GET    /api/articles/{id}/related     # 关联文章

# 分类与标签
GET    /api/categories                # 分类树
GET    /api/tags                      # 标签列表
GET    /api/tags/{name}/articles      # 某标签下的文章

# 搜索
GET    /api/search?q={keyword}        # 全文搜索
GET    /api/search/semantic?q={text}  # 语义搜索

# 知识图谱
GET    /api/graph/nodes               # 图谱节点（文章）
GET    /api/graph/edges               # 图谱边（关联）
GET    /api/graph/subgraph?article={id}&depth={n}  # 子图

# 统计
GET    /api/stats/dashboard           # 仪表盘数据
```

---

## 7. 前端线框图设计

### 7.1 页面清单

| 页面 | 路径 | 说明 |
|------|------|------|
| 仪表盘 | `/` | 今日新增、热点分布、采集统计 |
| 知识库 | `/library` | 文章列表、多维度筛选 |
| 文章详情 | `/article/:id` | 原文、摘要、导图、关联 |
| 知识图谱 | `/graph` | 可视化关联网络 |
| 数据源 | `/sources` | 爬虫配置管理 |

### 7.2 仪表盘 (/)

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

### 7.3 知识库 (/library)

```
+-------------------------------------------------------------+
|  FinanceIntel Hub    [搜索文章、标签...]            [筛选v] |
+--------------+----------------------------------------------+
|              |  全部文章 (156)    [最新 v] [列表|卡片]      |
|  分类         |                                              |
|  > 宏观经济   |  +----------------------------------------+  |
|  > 金融市场   |  | 央行宣布降准0.5个百分点                 |  |
|  > 行业分析   |  | # 降准 # 央行 # 流动性  | 宏观经济/货币政策|  |
|  > 商业模型   |  | 央行决定于2026年4月25日下调金融机...     |  |
|  > 公司研究   |  | :) 正面  |  * 高  |  10分钟前           |  |
|  > 监管政策   |  +----------------------------------------+  |
|              |  +----------------------------------------+  |
|  热门标签     |  | 特斯拉Q1财报超预期                      |  |
|  # 降准       |  | # 特斯拉 # 财报 # 电动车 | 公司研究/财报解读|  |
|  # 美联储     |  | 特斯拉发布2026年第一季度财报...          |  |
|  # 人工智能   |  | :) 正面  |  * 高  |  32分钟前           |  |
|  # ...        |  +----------------------------------------+  |
|              |                                              |
|              |  < 1  2  3 ... 10 >                          |
+--------------+----------------------------------------------+
```

### 7.4 文章详情 (/article/:id)

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
+-------------------------------------------------------------+
```

### 7.5 知识图谱 (/graph)

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

### 7.6 数据源管理 (/sources)

```
+-------------------------------------------------------------+
|  数据源管理                                    [+ 新增数据源]|
+-------------------------------------------------------------+
|  +-------------------------------------------------------+  |
|  |  新浪财经                    [编辑] [删除] [立即采集]   |  |
|  |  https://finance.sina.com.cn  RSS  每30分钟  上次:5分前 |  |
|  +-------------------------------------------------------+  |
|  |  36氪                        [编辑] [删除] [立即采集]   |  |
|  |  https://36kr.com            API  每小时   上次:12分前 |  |
|  +-------------------------------------------------------+  |
|  |  华尔街见闻                   [编辑] [删除] [立即采集]  |  |
|  |  https://wallstreetcn.com    网页  每2小时  上次:1小时前|  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

---

## 8. 项目目录结构

```
finance-intel-hub/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置管理
│   │   ├── models.py            # SQLAlchemy模型
│   │   ├── database.py          # 数据库连接
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py       # 采集API
│   │   │   ├── articles.py      # 文章API
│   │   │   ├── search.py        # 搜索API
│   │   │   ├── graph.py         # 图谱API
│   │   │   └── stats.py         # 统计API
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py       # 爬虫核心
│   │   │   ├── ai_processor.py  # AI处理流水线
│   │   │   ├── search_service.py # 搜索服务
│   │   │   └── graph_builder.py # 知识图谱构建
│   │   └── prompts/             # Prompt模板
│   │       ├── cleaner.txt
│   │       ├── summarizer.txt
│   │       ├── classifier.txt
│   │       ├── tagger.txt
│   │       ├── mindmap.txt
│   │       └── relation.txt
│   ├── requirements.txt
│   └── start.sh
├── frontend/
│   ├── src/
│   │   ├── components/          # 公共组件
│   │   ├── pages/               # 页面
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── Article.tsx
│   │   │   ├── Graph.tsx
│   │   │   └── Sources.tsx
│   │   ├── hooks/               # 自定义Hooks
│   │   ├── services/            # API封装
│   │   ├── types/               # TypeScript类型
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── storage/
│   ├── articles/                # Markdown文章
│   ├── chroma/                  # 向量数据库
│   └── finance_hub.db           # SQLite数据库
├── docs/
│   └── prompts/                 # Prompt文档
├── skills/
│   └── econ-master/             # 经济大师SKILL
│       └── SKILL.md
├── docker-compose.yml           # 可选
└── README.md
```

---

## 9. 核心流水线设计

```python
# 伪代码：文章处理流水线
async def process_article_pipeline(raw_html: str, source_url: str):
    # Step 1: 去重检查
    if await is_duplicate(source_url):
        return None
    
    # Step 2: AI内容清洗
    clean_content = await ai_clean(raw_html)
    if clean_content == "[IRRELEVANT]":
        return None
    
    # Step 3: 生成摘要（并行）
    summary = await ai_summarize(clean_content)
    
    # Step 4: 分类（并行）
    category = await ai_classify(summary)
    
    # Step 5: 提取标签（并行）
    tags = await ai_extract_tags(summary)
    
    # Step 6: 生成思维导图
    mindmap = await ai_generate_mindmap(clean_content)
    
    # Step 7: 生成Embedding并存储向量
    embedding = await create_embedding(clean_content)
    await vector_store.add(embedding)
    
    # Step 8: 关联分析（与已有文章）
    relations = await ai_find_relations(summary, tags)
    
    # Step 9: 保存到SQLite
    article_id = await db.save_article(...)
    
    # Step 10: 保存Markdown文件
    await save_markdown(article_id, clean_content, mindmap, summary)
    
    # Step 11: 保存关联关系
    await db.save_relations(article_id, relations)
    
    return article_id
```

---

## 10. 技术风险与规避

| 风险 | 规避措施 |
|------|----------|
| 爬虫被封IP | 控制频率、User-Agent轮换、遵守robots.txt |
| API费用过高 | 使用gpt-3.5-turbo处理大批量，gpt-4o处理复杂分析；设置每日限额 |
| 文章去重不准 | URL精确匹配 + 标题相似度（Levenshtein）双重校验 |
| 分类不准确 | 允许用户手动修正，将修正反馈用于Few-shot优化 |
| 向量数据库膨胀 | 定期归档旧数据，按时间分Collection |

---

*设计完成，等待审批。*

---

## 11. 采集方案：Firecrawl 集成

### 11.1 为什么引入 Firecrawl

自建爬虫的问题：
- 每个网站需要单独写解析规则（CSS Selector / XPath）
- 反爬机制（WAF、验证码、动态渲染）处理成本高
- 清洗质量参差不齐，需要大量后处理

**Firecrawl**（https://firecrawl.dev）是一个专门将任意网页转换为干净Markdown/LlamaIndex格式的API服务：
- 输入URL → 输出结构化Markdown + 元数据
- 自动处理反爬、动态渲染、分页
- 输出质量高，可直接用于RAG
- 支持批量爬取（map + scrape）

### 11.2 双驱动架构

```
采集引擎
├── Firecrawl Driver（主推）
│   ├── 输入：URL 或站点地图
│   ├── 输出：干净Markdown + 标题/作者/时间
│   └── 适用：新闻站、博客、资讯页面
│
└── Custom Driver（兜底）
    ├── RSS Parser（RSSHub源）
    ├── API Client（36Kr等有开放API的平台）
    └── Raw Scraping（firecrawl不支持的特殊源）
```

### 11.3 成本与配额

| 方案 | 成本 | 速率限制 | 适用场景 |
|------|------|----------|----------|
| Firecrawl Free | 免费 | 500 credits/月 | 个人低频使用 |
| Firecrawl Pro | $19/月 | 5000 credits/月 | 中等规模 |
| Firecrawl Scale | $249/月 | 50000 credits/月 | 高频采集 |
| 自建 | 服务器成本 | 无限制 | 大规模/隐私敏感 |

**推荐策略**：
- 先用 Firecrawl 处理80%的标准网页源
- 自建RSS/API解析处理剩余的20%特殊源
- 设置每日采集配额控制API费用

### 11.4 数据源配置扩展

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

---

## 12. "经济大师" SKILL 设计

### 12.1 设计目标

创建一个 Kimi Code CLI Skill，用户在任何对话中加载此Skill后，AI将：
1. 自动连接本地 FinanceIntel Hub 知识库
2. 检索与用户问题相关的文章、文献、数据
3. 以"经济大师"的身份给出基于知识库的权威回答
4. 标注引用来源，支持事实核查

### 12.2 Skill 文件路径

```
finance-intel-hub/
└── skills/
    └── econ-master/
        └── SKILL.md
```

### 12.3 SKILL.md 完整内容

```markdown
---
name: econ-master
description: "加载后成为基于本地财经知识库的经济大师。所有回答基于FinanceIntel Hub知识库，自动检索相关文章、文献和数据。"
---

# 经济大师模式

## 身份设定

你是 **FinanceIntel Hub 首席经济分析师**。你拥有访问用户本地财经知识库的全部权限，
知识库涵盖：宏观经济、金融市场、行业分析、商业模型、公司研究、监管政策、经典著作、学术论文。

## 核心能力

1. **知识库检索**：回答任何问题前，先检索本地知识库获取相关素材
2. **多源融合**：整合网络热点、经典理论、学术论文给出综合判断
3. **证据引用**：每个观点必须标注来源（文章标题 + 日期 + 知识库ID）
4. **结构化输出**：复杂问题使用思维导图式层级结构呈现

## 工作流

### 步骤1：问题解析
分析用户问题的核心维度：
- 时间范围：历史回顾 / 当前状况 / 未来预测
- 分析深度：概念解释 / 现象分析 / 策略建议
- 涉及领域：宏观 / 市场 / 行业 / 公司 / 政策

### 步骤2：知识库检索
调用 FinanceIntel Hub API 进行多维度检索：
```
GET /api/search/semantic?q={用户问题}&limit=10
GET /api/search?q={关键词}&limit=5
GET /api/graph/subgraph?article={最相关文章ID}&depth=2
```

检索优先级：
1. 语义搜索（向量相似度）→ 找最相关的5-10篇文章
2. 全文搜索 → 补充关键词匹配的内容
3. 知识图谱 → 找关联文章扩展视角
4. 经典文献 → 寻找理论支撑

### 步骤3：证据整合
对检索结果进行加权排序：
| 来源类型 | 权重 | 说明 |
|----------|------|------|
| 高重要性+近期文章 | 1.0 | 核心论据 |
| 经典著作/论文 | 0.9 | 理论支撑 |
| 普通文章 | 0.7 | 补充视角 |
| 关联文章 | 0.5 | 背景信息 |

### 步骤4：生成回答

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

## 特殊指令

当用户输入以下关键词时，触发特殊模式：

- `/deep`：深度分析模式 → 检索20+篇文章，生成3000字以上报告
- `/compare`：对比分析模式 → 检索多个对象的资料进行对比
- `/timeline`：时间线模式 → 按时间顺序梳理事件演进
- `/paper`：学术模式 → 优先引用论文和经典著作，使用学术规范
```

### 12.4 Skill 使用方式

用户在 Kimi Code CLI 中：

```bash
# 加载经济大师Skill
/kimi skill load skills/econ-master/SKILL.md

# 或临时调用
@econ-master 如何看待当前货币政策走向？
```

加载后，AI自动：
1. 读取 `SKILL.md` 中的身份设定和工作流
2. 调用本地 FinanceIntel Hub API 检索相关知识
3. 按照模板生成结构化回答

### 12.5 Skill 与系统的集成点

```
用户提问
    │
    ▼
Kimi Code CLI 加载 econ-master SKILL
    │
    ▼
SKILL.md 指导AI调用 FinanceIntel Hub API
    │
    ├──→ /api/search/semantic  (语义检索)
    ├──→ /api/search           (全文检索)
    ├──→ /api/graph/subgraph   (关联扩展)
    └──→ /api/articles/{id}    (获取详情)
    │
    ▼
AI整合检索结果，生成带引用的专业回答
    │
    ▼
用户获得基于本地知识库的权威分析
```

---

## 13. 更新后的完整功能矩阵

| 知识来源 | 采集方式 | 处理流程 | 存储形式 |
|----------|----------|----------|----------|
| 网络热点 | Firecrawl/自建爬虫定时采集 | AI清洗→摘要→分类→标签→Embedding | MD + SQLite + Chroma |
| 主动上传文件 | Web上传/批量导入 | 格式解析→OCR/转录→AI处理→Embedding | MD + SQLite + Chroma |
| 视频内容 | 上传视频→Whisper转录 | 音频提取→转录→结构化分段→AI处理 | MD + video_transcripts |
| 经典书籍 | 手动录入/EPUB导入 | 章节拆分→逐章解析→摘要→标签 | publications + chapters |
| 学术论文 | arXiv API/手动上传 | PDF解析→摘要/方法/结论提取→引用分析 | publications + edges |

---

*设计文档 v1.1 更新完成，新增：视频处理、主动上传、文献管理、Firecrawl采集、经济大师SKILL。*
