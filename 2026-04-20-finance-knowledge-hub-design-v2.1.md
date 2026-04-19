# FinanceIntel Hub — 财经智识库系统设计文档

> 版本：v2.1  
> 日期：2026-04-20  
> 状态：待审批  
> 基于 v2.0 增补：SKILL 持续进化、多端适配、云迁移、类目扩展

---

## V2.1 变更摘要

| 新增/变更 | 说明 |
|-----------|------|
| **新增 §12：SKILL 持续进化机制** | 用户反馈闭环 + 记忆层 + Prompt 自动优化，让 AI 越用越懂你 |
| **新增 §13：多端策略** | Web 响应式 + PWA + 原生 App 三步走，手机电脑都能用 |
| **新增 §14：云迁移路径** | 数据库/向量/文件三层云化方案，只改配置不改代码 |
| **新增 §15：知识类目扩展** | 不限于财经，任何知识领域都可以加进来 |
| **更新 §16：升级路线图** | 新增第四阶段"云端+多端" |
| **更新 §7：数据库** | 新增 SKILL 反馈表、记忆表、知识领域表 |

> V2.0 的第 0-11 节内容不变，以下只列出新增和变更的部分。完整基础设计请参阅 V2.0。

---

## 0. 用大白话讲清楚这个项目（V2.1 补充）

### V2.0 回顾

FinanceIntel Hub 是一个帮你自动收集财经新闻、AI 整理、方便查找的个人知识库。（详见 V2.0 第 0 节）

### V2.1 新增了什么？

V2.0 的"经济大师"SKILL 是一个**静态的 AI 助手**——你问它问题，它翻知识库给你答案。但它不会"长记性"，不会知道你关心什么，也不会越来越聪明。

V2.1 加了四个重要的东西：

#### 1. AI 会"长记性"了

打个比方：V2.0 的经济大师像一个**每天都是第一天上班的新员工**——你每次问它问题，它都从零开始找资料。

V2.1 的经济大师像一个**跟了你三年的私人分析师**：
- 它记得你关心"央行货币政策"和"新能源行业"
- 它记得你上次问过降准的问题，这次会主动关联
- 它记得你喜欢简洁的回答，而不是长篇大论
- 你告诉它"这个回答不太对"，下次它会改进

具体怎么做？很简单：
- 你给每个回答**点个赞或踩**（就像朋友圈点赞一样简单）
- 你可以**修改 AI 的分类/标签**，AI 会学习你的修正
- 系统自动记录你的**提问偏好**和**关注领域**

#### 2. 手机上也能用了

V2.0 只能在电脑浏览器里用。V2.1 考虑了三步：
1. **现在**：网页做成"手机友好"的——手机打开浏览器也能正常看，不会乱排版
2. **下一步**：做成 PWA（渐进式Web应用）——可以"安装"到手机桌面，像一个 App 一样打开，还能离线看文章
3. **远期**：如果真的需要推送通知、更好的手机体验，可以做原生 App

#### 3. 数据可以搬到云上

V2.0 所有数据都在你自己电脑上。V2.1 设计了一条"搬家路线"：
- **现在**：数据在本地（你的电脑），免费，速度快
- **以后**：如果你想在手机上看、或者换了电脑也能用，可以把数据搬到云上
- **怎么搬**：改一行配置（数据库地址从"本地"改成"云端"），运行一条命令，完成

不需要改任何代码，因为我们从一开始就设计好了这个"搬家通道"。

#### 4. 不只是财经——未来可以加任何知识领域

V2.0 的分类体系只有财经（宏观经济、金融市场、行业分析……）。V2.1 设计了一个"领域扩展"机制：

比如你未来想加一个"科技"知识库：
1. 新建一个知识领域："科技前沿"
2. 定义它的分类体系：AI/芯片/量子计算/太空科技……
3. 配对应的数据源：36氪科技频道、机器之心、ArXiv……
4. AI 自动用对应领域的方式来分类和分析

就像在图书馆新开了一个"科技区"，有自己的书架分类，但共用同一个搜索系统和借阅卡。

---

## 12. SKILL 持续进化机制（新增）

### 12.1 用大白话说：为什么 SKILL 能越来越聪明？

```
普通的 AI 助手：
  你问 → AI 回答 → 结束

经济大师 SKILL（V2.1）：
  你问 → AI 回答 → 你反馈（好/不好/修改） → AI 记住 → 下次更好

这就像：
  第 1 次用：AI 是应届生，按教科书回答
  用了 1 个月：AI 知道你关心什么，回答更有针对性
  用了 3 个月：AI 像私人分析师，主动告诉你"这个事和你上次关心的XX有关"
```

### 12.2 进化的三个层次

```
┌─────────────────────────────────────────────────────┐
│  第三层：Prompt 自我优化                              │
│  系统根据大量反馈数据，自动挑选更好的 Prompt 版本      │
│  （A/B 测试：同一个任务用两个 Prompt，看哪个得分高）    │
├─────────────────────────────────────────────────────┤
│  第二层：用户记忆                                     │
│  记住你关心的领域、提问习惯、偏好的回答风格            │
│  （下次回答时，自动注入你的偏好信息）                   │
├─────────────────────────────────────────────────────┤
│  第一层：反馈学习                                     │
│  你对每个回答打分 / 修正 AI 的分类和标签               │
│  （系统把修正积累下来，作为 Few-shot 样本优化 Prompt）  │
└─────────────────────────────────────────────────────┘
```

### 12.3 第一层：反馈学习

#### 用户能做的操作

| 操作 | 场景 | 系统怎么用 |
|------|------|-----------|
| 👍 / 👎 点赞/踩 | 对"经济大师"的回答或文章摘要 | 统计每个 Prompt 版本的好评率 |
| ✏️ 修改分类 | AI 把文章分到"宏观经济"，你改成"金融市场" | 记录修正对，作为分类 Prompt 的 Few-shot 样本 |
| ✏️ 修改标签 | AI 提取的标签不够准，你加了/删了几个 | 记录修正对，优化标签 Prompt |
| 📝 补充评论 | 对回答写一句评价："缺少了对比分析" | 系统分析评论中的高频改进方向 |

#### 反馈数据怎么变成"聪明"

```
用户修正：AI 把文章分到"宏观经济/货币政策"
         用户改为"金融市场/债券市场"
              │
              ▼
系统记录：{原始输入: "...", AI输出: "宏观经济/货币政策", 
          用户修正: "金融市场/债券市场"}
              │
              ▼
积累到 10 条同类修正后，自动加入分类 Prompt 的 Few-shot 样本：
  "注意：以下类型的文章常被错误分类，请参考这些修正案例：
   案例1：标题=xxx → 正确分类=金融市场/债券市场
   案例2：..."
              │
              ▼
下次分类同类文章时，AI 会参考这些修正，减少同样的错误
```

### 12.4 第二层：用户记忆

SKILL 会维护一个"用户画像"，记住你的偏好：

```yaml
# data/skill_memory/user_profile.yaml（自动维护，你不需要手动编辑）
focus_areas:                     # 你最关心的领域（按提问频率自动排序）
  - 宏观经济/货币政策
  - 行业分析/新能源
  - 公司研究/财报解读

recent_topics:                   # 你最近问过的主题
  - "央行降准对A股的影响"
  - "特斯拉和比亚迪的竞争格局"

answer_preferences:              # 你偏好的回答风格
  length: concise                # concise | detailed（根据反馈自动学习）
  style: data_driven             # data_driven | narrative | academic
  language: zh                   # 回答语言

correction_patterns:             # 你常见的修正模式
  - "倾向于把债券相关文章从宏观经济移到金融市场"
```

当你问"经济大师"问题时，系统会自动把这个画像注入 Prompt：

```
# SKILL 回答时的实际 Prompt（用户看不到，后台自动拼接）

System: 你是 FinanceIntel Hub 首席经济分析师...

# ↓ 自动注入的用户记忆
用户偏好信息：
- 该用户最关注：宏观经济/货币政策、新能源行业
- 该用户偏好简洁的回答风格，重视数据
- 该用户最近关注：央行降准、新能源竞争
- 请根据这些偏好调整回答的重点和风格

User: 如何看待当前货币政策走向？
```

### 12.5 第三层：Prompt A/B 测试

```
同一个任务（比如"文章分类"），系统可以同时运行两个版本的 Prompt：

Prompt v1（原版）  ──→ 分类结果A  ──→ 用户反馈率 72% 好评
Prompt v2（优化版）──→ 分类结果B  ──→ 用户反馈率 89% 好评

当 v2 的好评率稳定高于 v1 超过 100 次评估后：
  → 自动把 v2 设为默认版本
  → v1 标记为"已淘汰"
  → 系统日志记录切换原因
```

### 12.6 SKILL.md（V2.1 完整版）

```markdown
---
name: econ-master
version: 3
description: 基于本地财经知识库的经济分析助手，支持持续学习和用户偏好适配
api_base: http://localhost:8000/api
memory_enabled: true
feedback_enabled: true
---

# 经济大师模式

## 身份

你是 FinanceIntel Hub 首席经济分析师。你可以访问用户的本地财经知识库。
你会根据用户的历史偏好和反馈来优化回答。

## 工作流

1. **加载记忆** → 读取用户画像和最近对话上下文
2. **解析问题** → 确定时间范围、分析深度、涉及领域
3. **检索知识库** → 调用 API 获取相关文章（优先用户关注领域）
4. **整合证据** → 按权重排序检索结果
5. **生成回答** → 基于用户偏好的风格输出
6. **等待反馈** → 用户可打分/修正，反馈自动记录

## 检索方式

```
# 语义搜索（主要）
GET {api_base}/search/semantic?q={用户问题}&limit=10

# 全文搜索（补充）
GET {api_base}/search?q={关键词}&limit=5

# 知识图谱扩展
GET {api_base}/graph/subgraph?article_id={id}&depth=2

# 读取用户记忆（新增）
GET {api_base}/skill/memory

# 读取领域相关的 Few-shot 样本（新增）
GET {api_base}/skill/examples?domain={领域}
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

---
💡 这个回答对你有帮助吗？ [👍 有用] [👎 不准确] [✏️ 补充]

## 约束

1. 不引用知识库中不存在的内容
2. 区分"最新数据"和"历史数据"
3. 预测性观点标注置信度（高/中/低）
4. 矛盾观点必须呈现双方论据
5. 用户修正过的分类/标签，后续遵循用户的判断

## 特殊指令

- `/deep` — 深度分析，检索20+篇，3000字以上
- `/compare` — 对比分析
- `/timeline` — 时间线梳理
- `/paper` — 学术模式，优先引用论文
- `/forget` — 清除用户记忆，重新开始（新增）
- `/profile` — 查看当前用户画像（新增）
```

### 12.7 进化机制总结

| 问题 | 答案 |
|------|------|
| SKILL 持续优化可行吗？ | **完全可行**。核心是：反馈数据 → Few-shot 样本 → Prompt 优化。不需要训练模型，只需要积累和管理好样本。 |
| 多久能看到效果？ | 大约积累 50-100 条反馈后，AI 的回答质量会有明显提升 |
| 用户需要做什么？ | 偶尔点个 👍👎，偶尔修正一下分类/标签，仅此而已 |
| 技术难度高吗？ | 不高。反馈收集是普通的 CRUD；Few-shot 注入就是往 Prompt 里加几行文字；A/B 测试是简单的比较逻辑 |

---

## 13. 多端策略：Web + 手机（新增）

### 13.1 三步走方案

```
┌─────────────────────────────────────────────────────────┐
│  第一步（MVP 就做）：响应式 Web                           │
│  ┌──────────┐  ┌──────────┐                              │
│  │  电脑看    │  │  手机看   │  ← 同一个网页，不同屏幕自动适配│
│  │  ┌──┬──┐  │  │  ┌────┐  │                              │
│  │  │  │  │  │  │  │    │  │                              │
│  │  │  │  │  │  │  ├────┤  │                              │
│  │  └──┴──┘  │  │  │    │  │                              │
│  └──────────┘  │  └────┘  │                              │
│                 └──────────┘                              │
│  技术：TailwindCSS 响应式样式                             │
│  成本：零额外开发，CSS 媒体查询搞定                        │
├─────────────────────────────────────────────────────────┤
│  第二步（阶段二做）：PWA（渐进式Web应用）                   │
│                                                         │
│  手机上"安装"到桌面，像 App 一样打开                       │
│  ✅ 离线可读已缓存的文章                                  │
│  ✅ 全屏模式，没有浏览器工具栏                             │
│  ✅ 可以接收推送通知（"今日有 5 篇重要文章"）              │
│  技术：Service Worker + manifest.json                    │
│  成本：2-3 天开发                                        │
├─────────────────────────────────────────────────────────┤
│  第三步（远期按需做）：原生 App                            │
│                                                         │
│  用 Capacitor 把 Web 打包成 iOS / Android App            │
│  ✅ 访问手机相机（拍文档直接入库）                         │
│  ✅ 本地推送通知                                          │
│  ✅ 更流畅的手机体验                                      │
│  技术：Capacitor（复用现有 React 代码，不用重写）          │
│  成本：1-2 周开发                                        │
└─────────────────────────────────────────────────────────┘
```

### 13.2 为什么不一开始就做 App？

| 方案 | 开发成本 | 维护成本 | 用户体验 |
|------|----------|----------|----------|
| 响应式 Web | 几乎为零 | 一份代码 | 够用（80分） |
| PWA | 2-3 天 | 一份代码 | 很好（90分） |
| Capacitor 打包 | 1-2 周 | 一份代码 | 优秀（95分） |
| React Native 原生 | 4-8 周 | 两份代码 | 最好（100分） |

**结论**：从响应式 Web 起步，到 PWA，最后按需做 Capacitor。全程共用一套 React 代码，不需要重写。

### 13.3 架构上需要做什么准备？

```
现在就做（MVP 阶段）：
✅ 前端用 TailwindCSS —— 天然支持响应式
✅ API 设计是 RESTful JSON —— 任何端都能调用
✅ 数据逻辑在后端 —— 前端只是"展示层"

阶段二做：
✅ 加 Service Worker —— 实现离线缓存
✅ 加 manifest.json —— 可安装到桌面
✅ 加推送 API —— /api/notifications

远期做：
✅ Capacitor 配置 —— 打包成 App
✅ 相机/文件 API 对接 —— 手机拍照入库
```

### 13.4 手机端页面适配

```
电脑端：左右两栏布局            手机端：单栏堆叠布局
┌────────┬─────────────┐      ┌──────────────────┐
│ 分类    │  文章列表     │      │  [搜索]  [筛选▼] │
│ 树     │  ┌────────┐  │      ├──────────────────┤
│        │  │ 文章1   │  │      │ 文章1             │
│ 热门   │  │ 文章2   │  │  →   │ 文章2             │
│ 标签   │  │ 文章3   │  │      │ 文章3             │
│        │  └────────┘  │      │ ...               │
└────────┴─────────────┘      └──────────────────┘
                               分类/标签折叠到顶部筛选按钮里
```

---

## 14. 云迁移路径（新增）

### 14.1 大白话版

```
现在（本地模式）：
  所有数据在你电脑上 → 免费，速度快，但只能在这台电脑上用

未来（云端模式）：
  数据在云服务器上 → 手机/电脑/任何设备都能用，但每月有少量费用

怎么切换？
  改一个配置文件里的几行地址，运行一条命令，完事。
  不需要改任何代码。
```

### 14.2 三层数据的云化方案

| 数据层 | 本地方案（现在） | 云端方案（未来） | 切换方式 |
|--------|-----------------|-----------------|----------|
| 结构化数据库 | SQLite（单文件） | Supabase PostgreSQL 或 Neon | 改 `DATABASE_URL` |
| 向量数据库 | ChromaDB（本地） | Pinecone 或 Qdrant Cloud | 改 `VECTOR_DB_URL` |
| 文件存储 | 本地 `data/` 目录 | AWS S3 或阿里云 OSS | 改 `STORAGE_BACKEND` |

### 14.3 配置切换示意

```bash
# ========== 本地模式（现在） ==========
DATABASE_URL=sqlite:///./data/hub.db
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/chroma
STORAGE_BACKEND=local
STORAGE_PATH=./data

# ========== 云端模式（未来） ==========
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/hub
VECTOR_DB=pinecone
PINECONE_API_KEY=xxx
PINECONE_INDEX=finance-hub
STORAGE_BACKEND=s3
S3_BUCKET=finance-hub-data
S3_REGION=ap-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

### 14.4 代码层面怎么做到"无痛切换"？

关键是**抽象层**——代码不直接跟 SQLite / ChromaDB / 文件系统打交道，而是跟一个"中间人"打交道：

```python
# server/src/db/engine.py —— 数据库抽象

from config import settings

# 这一行代码同时支持 SQLite 和 PostgreSQL
# 因为 SQLAlchemy 通过 URL 格式自动识别数据库类型
engine = create_engine(settings.DATABASE_URL)
# settings.DATABASE_URL = "sqlite:///..."  → 用 SQLite
# settings.DATABASE_URL = "postgresql://..." → 用 PostgreSQL
# 代码完全一样，一行都不用改
```

```python
# server/src/core/storage.py —— 文件存储抽象（新增）

class StorageBackend:
    """存储后端抽象：本地和云端共用同一个接口"""

    def save(self, path: str, content: bytes): ...
    def load(self, path: str) -> bytes: ...
    def delete(self, path: str): ...

class LocalStorage(StorageBackend):
    """本地文件系统"""
    ...

class S3Storage(StorageBackend):
    """AWS S3 / 阿里云 OSS"""
    ...

# 根据配置自动选择
def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == "local":
        return LocalStorage(settings.STORAGE_PATH)
    elif settings.STORAGE_BACKEND == "s3":
        return S3Storage(settings.S3_BUCKET)
```

### 14.5 云端费用参考

| 服务 | 免费额度 | 预估月费（个人使用） |
|------|----------|---------------------|
| Supabase（数据库） | 500MB + 50k 行 | 免费或 $25/月 |
| Neon（数据库） | 3GB | 免费 |
| Pinecone（向量） | 100k 向量 | 免费或 $70/月 |
| AWS S3（文件） | 5GB | < $1/月 |

个人使用的前期完全可以在免费额度内。

### 14.6 数据迁移命令

```makefile
# Makefile 新增

db-export:    ## 导出本地数据库为 SQL
	sqlite3 data/hub.db .dump > data/export.sql

db-import:    ## 导入数据到云端数据库（需先配置 DATABASE_URL）
	psql $(DATABASE_URL) < data/export.sql

migrate-cloud: ## 一键迁移到云端
	@echo "1. 导出本地数据..."
	make db-export
	@echo "2. 导入到云端数据库..."
	make db-import
	@echo "3. 同步文件到 S3..."
	aws s3 sync data/articles/ s3://$(S3_BUCKET)/articles/
	@echo "4. 迁移完成！请更新 .env 中的配置指向云端。"
```

---

## 15. 知识类目扩展机制（新增）

### 15.1 大白话版

```
现在：知识库只有"财经"一个大类
     └── 宏观经济 / 金融市场 / 行业分析 / ...

未来：知识库可以有多个大类
     ├── 财经（已有）
     │   └── 宏观经济 / 金融市场 / ...
     ├── 科技（新加）
     │   └── 人工智能 / 芯片半导体 / 量子计算 / ...
     ├── 法律（新加）
     │   └── 合同法 / 知识产权 / 公司法 / ...
     └── 任何你想要的领域...

怎么加？不用改代码。
  1. 在"知识领域"管理页面点"新增"
  2. 填领域名称 + 分类体系
  3. 配数据源
  4. 完成——AI 自动用这个领域的方式来处理新文章
```

### 15.2 知识领域数据模型

```
┌─────────────────────────────────────────┐
│  knowledge_domains（知识领域表）           │
│  ┌───────────────────────────────────┐  │
│  │ id: 1                             │  │
│  │ name: "财经"                      │  │
│  │ slug: "finance"                   │  │
│  │ description: "经济金融商业知识"    │  │
│  │ icon: "💰"                        │  │
│  │ prompt_context: "你是财经分析专家" │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ id: 2                             │  │
│  │ name: "科技"                      │  │
│  │ slug: "tech"                      │  │
│  │ description: "科技前沿知识"       │  │
│  │ icon: "🔬"                        │  │
│  │ prompt_context: "你是科技产业分析师"│  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ 一个领域有多个分类
         ▼
┌─────────────────────────────────────────┐
│  categories（分类表——V2.0 已有，加 domain_id）│
│  domain_id: 1 → 宏观经济/货币政策/...     │
│  domain_id: 2 → 人工智能/芯片半导体/...   │
└─────────────────────────────────────────┘
```

### 15.3 扩展对 Prompt 的影响

每个知识领域可以有自己的"领域上下文"，自动注入到所有 Prompt 中：

```yaml
# 财经领域的分类 Prompt
system: |
  你是一名财经内容分类专家...  ← 领域上下文自动注入

# 科技领域的分类 Prompt（复用同一个模板，注入不同上下文）
system: |
  你是一名科技产业分类专家...  ← 领域上下文自动注入
```

这样做的好处：
- **Prompt 模板只有一套**，不需要每个领域写一套
- **领域差异通过配置注入**，不需要改代码
- **新增领域 = 填一个表单**，不需要开发

### 15.4 SKILL 的多领域扩展

当知识领域扩展后，SKILL 也可以扩展：

```
skills/
├── econ-master/          # 经济大师（已有）
│   └── SKILL.md
├── tech-analyst/         # 科技分析师（新增）
│   └── SKILL.md
└── general-expert/       # 通用知识专家（新增——跨领域综合分析）
    └── SKILL.md
```

每个 SKILL 共用同一套 API，只是 `SKILL.md` 里的身份设定和检索偏好不同。

---

## 7. 数据库设计 — V2.1 新增表

> 以下表是在 V2.0 基础上新增的，V2.0 的所有表保持不变。

```sql
-- ============================================================
-- SKILL 进化相关（V2.1 新增）
-- ============================================================

-- 知识领域（支持多领域扩展）
CREATE TABLE knowledge_domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- "财经"、"科技"、"法律"
    slug TEXT NOT NULL UNIQUE,       -- "finance"、"tech"、"law"
    description TEXT,
    icon TEXT,                       -- emoji 图标
    prompt_context TEXT,             -- 注入 Prompt 的领域上下文
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKILL 回答反馈
CREATE TABLE skill_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,        -- "econ-master"
    query TEXT NOT NULL,             -- 用户的问题
    response_summary TEXT,           -- AI 回答的摘要（前200字）
    rating INTEGER CHECK(rating IN (-1, 0, 1)),  -- -1=差 0=一般 1=好
    comment TEXT,                    -- 用户的补充评论
    prompt_version INTEGER,          -- 使用的 Prompt 版本号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户对 AI 处理结果的修正记录
CREATE TABLE corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    field TEXT NOT NULL,             -- "primary_category" | "secondary_category" | "tags" | "sentiment"
    original_value TEXT,             -- AI 原始输出
    corrected_value TEXT,            -- 用户修正后的值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKILL 用户记忆（偏好 + 上下文）
CREATE TABLE skill_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,        -- "focus_areas" | "answer_preferences" | "recent_topics"
    value TEXT NOT NULL,             -- JSON 值
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prompt A/B 测试记录
CREATE TABLE prompt_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_name TEXT NOT NULL,       -- "classifier"、"summarizer"
    version_a INTEGER NOT NULL,
    version_b INTEGER NOT NULL,
    total_trials INTEGER DEFAULT 0,
    version_a_wins INTEGER DEFAULT 0,
    version_b_wins INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running' CHECK(status IN ('running', 'concluded')),
    winner INTEGER,                  -- 胜出版本号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    concluded_at TIMESTAMP
);
```

### V2.0 表的修改

```sql
-- categories 表新增 domain_id 字段（通过 Alembic 迁移添加）
ALTER TABLE categories ADD COLUMN domain_id INTEGER REFERENCES knowledge_domains(id);

-- articles 表新增 domain_id 字段
ALTER TABLE articles ADD COLUMN domain_id INTEGER REFERENCES knowledge_domains(id);

-- sources 表新增 domain_id 字段
ALTER TABLE sources ADD COLUMN domain_id INTEGER REFERENCES knowledge_domains(id);

-- 新索引
CREATE INDEX idx_skill_feedback_skill ON skill_feedback(skill_name);
CREATE INDEX idx_skill_feedback_rating ON skill_feedback(rating);
CREATE INDEX idx_corrections_article ON corrections(article_id);
CREATE INDEX idx_articles_domain ON articles(domain_id);
CREATE INDEX idx_categories_domain ON categories(domain_id);
```

---

## 8. API 设计 — V2.1 新增接口

> 在 V2.0 的 API 基础上新增以下接口。

```yaml
# ── SKILL 进化（新增）─────────────
POST   /api/skill/feedback            # 提交回答反馈（👍👎）
GET    /api/skill/memory              # 读取用户记忆/画像
PUT    /api/skill/memory              # 更新用户记忆
GET    /api/skill/examples?domain={d} # 获取领域 Few-shot 样本

# ── 修正（新增）─────────────────
POST   /api/articles/{id}/correct     # 提交对文章分类/标签的修正

# ── 知识领域（新增）─────────────
GET    /api/domains                   # 所有知识领域
POST   /api/domains                   # 新增知识领域
PUT    /api/domains/{id}              # 编辑知识领域
DELETE /api/domains/{id}              # 删除知识领域
GET    /api/domains/{id}/categories   # 某领域的分类树

# ── Prompt 管理（新增）──────────
GET    /api/prompts                   # 所有 Prompt 及版本
GET    /api/prompts/{name}/stats      # 某 Prompt 的好评率统计
```

---

## 4. 项目目录结构 — V2.1 变更

```
finance-intel-hub/
│
├── server/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py
│   │   │   ├── articles.py
│   │   │   ├── upload.py
│   │   │   ├── search.py
│   │   │   ├── graph.py
│   │   │   ├── stats.py
│   │   │   ├── skill.py           # 新增：SKILL 反馈 + 记忆 API
│   │   │   └── domains.py         # 新增：知识领域管理 API
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py
│   │   │   ├── processor.py
│   │   │   ├── uploader.py
│   │   │   ├── search.py
│   │   │   ├── graph.py
│   │   │   ├── scheduler.py
│   │   │   ├── feedback.py        # 新增：反馈收集 + Few-shot 样本管理
│   │   │   ├── memory.py          # 新增：用户记忆管理
│   │   │   └── storage.py         # 新增：存储抽象层（本地/S3）
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── models.py          # 更新：新增 V2.1 的表
│   │   │   └── migrations/
│   │   │       ├── env.py
│   │   │       └── versions/
│   │   │
│   │   └── prompts/
│   │       ├── v1/                 # Prompt 版本1
│   │       ├── v2/                 # Prompt 版本2（A/B 测试用）
│   │       └── loader.py
│   │
│   ├── tests/
│   │   ├── test_processor.py
│   │   ├── test_crawler.py
│   │   ├── test_api.py
│   │   ├── test_feedback.py       # 新增
│   │   └── test_storage.py        # 新增
│   │
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── web/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── ArticleDetail.tsx
│   │   │   ├── Graph.tsx
│   │   │   ├── Sources.tsx
│   │   │   ├── Upload.tsx
│   │   │   └── Domains.tsx        # 新增：知识领域管理页面
│   │   ├── components/
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── TagList.tsx
│   │   │   ├── CategoryTree.tsx
│   │   │   ├── MindmapView.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── FeedbackButtons.tsx # 新增：👍👎 反馈组件
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── store/
│   │   └── types/
│   │
│   ├── index.html
│   ├── manifest.json              # 新增：PWA 配置
│   ├── sw.js                      # 新增：Service Worker（PWA 离线缓存）
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts         # 明确：用 TailwindCSS 做响应式
│   └── vite.config.ts
│
├── data/
│   ├── articles/
│   ├── uploads/
│   ├── chroma/
│   ├── skill_memory/              # 新增：SKILL 用户画像缓存
│   └── hub.db
│
├── skills/
│   └── econ-master/
│       └── SKILL.md
│
├── docs/
├── .env.example
├── .gitignore
├── Makefile
├── capacitor.config.ts            # 远期：Capacitor 打包配置
└── README.md
```

---

## 13. 配置与启动 — V2.1 更新

### 环境变量 (.env.example)

```bash
# ── AI 服务 ──────────────────────
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL_PRIMARY=gpt-4o
OPENAI_MODEL_FAST=gpt-4o-mini

# ── 采集服务 ──────────────────────
FIRECRAWL_API_KEY=fc-xxx

# ── 数据库 ────────────────────────
# 本地模式（默认）
DATABASE_URL=sqlite:///./data/hub.db
# 云端模式（取消注释即切换）
# DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/hub

# ── 向量数据库 ────────────────────
# 本地模式（默认）
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/chroma
# 云端模式（取消注释即切换）
# VECTOR_DB=pinecone
# PINECONE_API_KEY=xxx
# PINECONE_INDEX=finance-hub

# ── 文件存储 ──────────────────────
# 本地模式（默认）
STORAGE_BACKEND=local
STORAGE_PATH=./data
# 云端模式（取消注释即切换）
# STORAGE_BACKEND=s3
# S3_BUCKET=finance-hub-data
# AWS_ACCESS_KEY_ID=xxx
# AWS_SECRET_ACCESS_KEY=xxx

# ── 服务端口 ──────────────────────
SERVER_PORT=8000

# ── SKILL 配置 ────────────────────
SKILL_FEEDBACK_ENABLED=true
SKILL_MEMORY_ENABLED=true
PROMPT_AB_TEST_ENABLED=false       # 阶段三开启
```

---

## 16. 升级路线图（V2.1 更新）

### 阶段一：MVP（第 2-3 周）

**目标**：跑通核心流程——采集 → AI 处理 → 存储 → 展示

```
做什么：
✅ 后端：FastAPI + SQLite + ChromaDB
✅ 采集：Firecrawl 对接 2-3 个财经源
✅ AI：清洗 + 摘要 + 分类 + 标签（四步流水线）
✅ 前端：仪表盘 + 知识库列表 + 文章详情
✅ 搜索：全文搜索（FTS5）
✅ 数据源管理
✅ 响应式布局（TailwindCSS，手机也能看）     ← V2.1 新增

不做什么：
❌ 知识图谱 / 语义搜索 / 文件上传 / 视频处理
❌ SKILL / 反馈 / 记忆
❌ 云端 / PWA / App
```

### 阶段二：增强（第 3-5 周）

**目标**：知识关联 + 多源输入 + 智能搜索 + PWA

```
新增：
✅ 思维导图 + 知识图谱可视化
✅ 语义搜索（ChromaDB 向量检索）
✅ 文件上传（PDF / Word / TXT / EPUB）
✅ 视频处理（Whisper 转录）
✅ PWA 支持（离线缓存 + 桌面安装）          ← V2.1 新增
✅ 👍👎 反馈按钮 + 修正功能                 ← V2.1 新增

架构不变，只加功能。
```

### 阶段三：智能化（第 5-8 周）

**目标**：知识库变成会进化的智能助手

```
新增：
✅ 经济大师 SKILL 上线
✅ SKILL 记忆层（用户画像 + 偏好学习）       ← V2.1 新增
✅ Few-shot 样本自动积累                     ← V2.1 新增
✅ Prompt A/B 测试机制                       ← V2.1 新增
✅ 文献管理（书籍 / 论文）
✅ 批量导入
✅ 知识领域管理页面                          ← V2.1 新增
```

### 阶段四：云端 + 多端（第 8-12 周）  ← V2.1 新增

**目标**：随时随地可用，数据安全上云

```
新增：
✅ 存储抽象层（LocalStorage / S3Storage）
✅ 数据库迁移到 Supabase PostgreSQL
✅ 向量数据库迁移到 Pinecone（按需）
✅ 文件迁移到 S3/OSS
✅ Capacitor 打包 iOS/Android App（按需）
✅ 新增第二个知识领域（如"科技"）验证扩展机制

架构变更：
🔄 SQLite → PostgreSQL
🔄 本地文件 → S3
🔄 ChromaDB → Pinecone（按需）
🔄 单进程 → 后台任务队列（如果处理量需要）
```

### 远期（第 12 周+）

| 方向 | 触发条件 | 做什么 |
|------|----------|--------|
| 多用户 | 需要分享给团队 | 加 `users` 表 + JWT 认证 |
| 多领域 SKILL | 知识库扩展到 3+ 领域 | 新增 `tech-analyst` 等 SKILL |
| 原生 App | PWA 体验不够好 | Capacitor 打包 |
| 自动化报告 | 日/周报需求 | 定时 AI 生成综合分析报告 |
| 插件市场 | 数据源类型太多 | `core/crawler.py` 改为插件注册机制 |

---

## 17. 技术风险与规避（V2.1 更新）

| 风险 | 规避措施 |
|------|----------|
| 爬虫被封 IP | 控制频率、Firecrawl 自带反封、遵守 robots.txt |
| AI API 费用过高 | gpt-4o-mini 跑量；gpt-4o 只做摘要/关联；设每日上限 |
| 文章去重不准 | URL 精确匹配 + 标题相似度双重校验 |
| AI 分类不准 | 用户修正 → Few-shot 样本积累 → Prompt 自动优化 |
| 向量数据库膨胀 | 定期归档，按月分 Collection |
| 数据库改表 | Alembic 迁移，自动生成升级脚本 |
| 云迁移数据丢失 | 迁移前自动备份；存储抽象层让切换无需改代码 |
| SKILL 记忆偏差 | `/forget` 命令可清除记忆；记忆有上限（最近 100 条交互） |
| 手机端体验差 | 从 MVP 就用 TailwindCSS 响应式；PWA 提供类 App 体验 |
| 多领域 Prompt 不准 | 每个领域独立的 Few-shot 样本库；A/B 测试自动选优 |

---

## 18. 你的问题的直接回答

### Q1：SKILL 持续优化机制可行吗？

**完全可行，而且不复杂。** 核心思路是"反馈驱动的 Prompt 优化"，不需要训练模型。

```
可行性分析：

技术难度：⭐⭐ （满分5星）
  - 反馈收集 = 普通的数据库写入
  - Few-shot 注入 = 往 Prompt 里拼接几行文字
  - 用户记忆 = 一个 JSON 存储
  - A/B 测试 = 简单的计数比较

效果预期：
  - 50 条反馈后 → 分类准确率明显提升
  - 100 条反馈后 → AI 开始适配你的偏好
  - 300 条反馈后 → 像一个懂你的私人分析师

成本：
  - 开发成本：1-2 周
  - 运行成本：几乎为零（反馈数据很小）
  - 用户成本：偶尔点个赞/踩，每次花 1 秒
```

### Q2：Web + 手机端考虑到了吗？

**V2.0 只是一句话提了，V2.1 已经完整设计了三步走方案。**（见第 13 节）

关键点：从 MVP 就用 TailwindCSS 做响应式，手机浏览器直接能用。后续 PWA → Capacitor App，全程共用一套代码。

### Q3：数据库迁移到云端考虑到了吗？

**V2.0 只提了 PostgreSQL，V2.1 已经设计了完整的三层云化方案。**（见第 14 节）

关键点：代码里用"抽象层"隔离，切换只需要改 `.env` 配置文件中的地址。SQLite → PostgreSQL、ChromaDB → Pinecone、本地文件 → S3，全部通过改配置切换。

### Q4：增加新知识类目考虑到了吗？

**V2.0 的分类表支持动态增删，但没有"领域"概念。V2.1 新增了 `knowledge_domains` 表，支持完全独立的知识领域。**（见第 15 节）

关键点：新增一个知识领域 = 填一个表单（名称 + 分类体系 + 数据源），不需要改代码，不需要重写 Prompt。

---

## 19. 测试策略（V2.1 更新）

```
V2.0 的测试内容保持不变，新增：

✅ 反馈写入和 Few-shot 样本生成是否正确
✅ 用户记忆的读写是否正确
✅ 存储抽象层：本地和 S3 接口一致性
✅ 知识领域 CRUD + Prompt 上下文注入
✅ 数据库迁移脚本（SQLite → PostgreSQL 是否兼容）
```

---

*V2.1 设计文档完成。主要新增：SKILL 持续进化机制（反馈闭环+用户记忆+Prompt 自动优化）、多端策略（响应式→PWA→App）、云迁移路径（三层抽象+配置切换）、知识类目扩展（多领域独立管理）。*
