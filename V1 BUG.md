# V1 BUG 清单与修复方案

生成时间：2026-04-20

这份文档基于当前仓库代码的静态审查、前后端接口契约核对、迁移脚本检查和测试代码对照整理。

说明：
- 本次结论重点是运行时 bug 和数据契约问题，不是格式或代码风格问题。
- 编辑器错误面板没有报错，但这不代表项目运行正确。
- 当前项目的主要风险集中在三条链路：采集入库、搜索索引、前后端字段契约。

## 审查结论

当前项目不是“完全跑不起来”，而是存在一批“能启动，但核心功能一执行就出错或结果不可信”的问题。

优先级排序如下：
- P0：直接影响核心流程，必须先修
- P1：功能能跑，但结果错误或页面异常
- P2：后续会放大为迁移风险或维护风险

---

## P0 级 BUG

### 1. 视频上传链路会写入不存在的模型字段

影响文件：
- server/src/core/video_processor.py
- server/src/db/models.py

问题：
- video_processor.py 中创建 Article 时使用了 `tags=processed.get("tags", [])`
- 但 Article 模型并没有 `tags` 列
- 同一个文件里创建 Article 时也没有导入 Article，本身就有运行时错误风险

影响：
- 媒体上传后转文章流程不稳定
- 可能直接抛异常，导致上传任务失败

修复方案：
1. 在 video_processor.py 中补齐 Article 导入
2. 删除对 `Article.tags` 的直接写入
3. 标签改为走 `Tag` + `ArticleTag` 关联表保存
4. 为媒体上传增加最小回归测试

---

### 2. 爬虫入库链路同样写了不存在的 Article 字段

影响文件：
- server/src/core/crawler.py
- server/src/db/models.py

问题：
- crawler.py 在创建 Article 时也使用了 `tags=processed.get("tags", [])`
- 但 Article 模型没有 tags 字段

影响：
- 采集流程存在运行时失败风险
- 即使不立即报错，标签也不会正确入库

修复方案：
1. crawler.py 中移除非法字段写入
2. 新增标签写入逻辑：先 upsert Tag，再写入 ArticleTag
3. 补充采集入库后的标签断言测试

---

### 3. 爬虫关系分析链路字段名不一致，知识图谱边无法正确写入

影响文件：
- server/src/core/crawler.py
- server/src/prompts/v1/relation.yaml

问题：
- relation Prompt 里定义返回字段是 `article_id`
- crawler.py 中取值时却使用 `target_article_id`
- 同时 crawler.py 中直接实例化 `KnowledgeEdge`，但函数内部没有导入该模型

影响：
- 文章关系边基本写不进去
- 图谱功能的数据基础不可靠
- 严重时采集后处理直接报错

修复方案：
1. 统一 Prompt 和代码里的字段名
2. 推荐统一为 `article_id`
3. crawler.py 中补齐 `KnowledgeEdge` 导入
4. 为关系分析增加端到端测试

---

### 4. AI 输出的分类结果没有真正写回数据库外键

影响文件：
- server/src/core/processor.py
- server/src/core/crawler.py
- server/src/db/models.py

问题：
- processor.py 返回的是分类名称：`primary_category`、`secondary_category`
- 数据库 Article 模型存的是 `primary_category_id`、`secondary_category_id`
- crawler.py 当前没有做“名称 -> 分类ID”的映射

影响：
- 分类筛选不可信
- 统计图表不可信
- 图谱类别展示不可信
- 前端页面展示经常为空

修复方案：
1. 在入库前根据分类名称查询 Category 表
2. 将名称映射成对应 ID 再写入 Article
3. 如果分类不存在，做兜底处理并记录 warning
4. 增加“分类名称映射到 ID”的单元测试

---

### 5. 结构化字段直接写入 Text 列，没有统一 JSON 序列化

影响文件：
- server/src/core/crawler.py
- server/src/core/video_processor.py
- server/src/db/models.py

问题：
以下字段本质上是数组或对象，但当前直接写入 Text 列：
- `key_points`
- `entities`
- `segments`

影响：
- 读取出来时格式不稳定
- 前端可能拿到字符串而不是数组
- 后续迁移 PostgreSQL 或做 schema 校验时问题会放大

修复方案：
1. 在写入边界统一 `json.dumps`
2. 在 API 返回层统一反序列化或改为显式 response schema
3. 所有这类字段都走统一工具函数，避免遗漏
4. 为文章详情接口增加字段类型断言测试

---

### 6. 全文搜索依赖的 `articles_fts` 表根本没有建出来

影响文件：
- server/src/api/search.py
- server/src/db/migrations/versions/001_initial.py

问题：
- search.py 中直接查询 `articles_fts`
- 但初始迁移文件没有创建 FTS5 虚拟表
- 也没有对应的同步触发器

影响：
- 全文搜索名义上存在，实际上只能依赖异常 fallback
- 搜索结果相关性和性能都不可靠

修复方案：
1. 新增 FTS5 表 `articles_fts`
2. 新增 insert/update/delete 同步触发器
3. 若不想改初始迁移，则新增补丁迁移文件
4. test_migrations.py 中补充 FTS 表存在性断言
5. test_api_search.py 中增加真实 FTS 命中测试

---

## P1 级 BUG

### 7. 文章接口返回原始 ORM 对象，前端需要的字段并没有真正提供

影响文件：
- server/src/api/articles.py
- web/src/components/ArticleCard.tsx
- web/src/pages/ArticleDetail.tsx

问题：
前端使用了：
- `article.primary_category`
- `article.secondary_category`
- `article.tags`

但后端 Article 模型实际只有：
- `primary_category_id`
- `secondary_category_id`
- 标签需要通过关联表查出

影响：
- 文章卡片显示空分类
- 详情页分类和标签显示不稳定

修复方案：
1. 不再直接返回 ORM 裸对象
2. 新建 ArticleResponse schema
3. 在接口层组装：分类名、标签数组、结构化字段
4. 前端统一按 schema 消费

---

### 8. 图谱节点点击跳到了不存在的路由

影响文件：
- web/src/pages/ArticleDetail.tsx
- web/src/App.tsx

问题：
- App.tsx 定义的详情页路由是 `/article/:id`
- 但图谱节点点击后跳转的是 `/articles/${nid}`

影响：
- 知识图谱交互失效

修复方案：
1. 把跳转路径统一改成 `/article/${nid}`
2. 增加一个最小前端 smoke 验证

---

### 9. 知识库页面的分类树永远是空的

影响文件：
- web/src/pages/Library.tsx
- web/src/store/index.ts
- server/src/main.py

问题：
- 前端 store 有 `categories`
- Library 页面也依赖它渲染分类树
- 但后端没有 categories API，也没有在 main.py 注册对应 router

影响：
- 分类筛选无法使用
- 左侧导航形同虚设

修复方案：
1. 新增 `/api/categories`
2. 可同时补 `/api/tags`
3. 在 main.py 注册 router
4. 前端在页面加载时主动拉取 categories

---

### 10. 修正接口把字符串直接写进分类外键

影响文件：
- server/src/api/articles.py

问题：
- `corrected_value` 是字符串
- 接口当前直接赋值给 `primary_category_id`

影响：
- SQLite 宽松类型下不一定立刻炸
- 未来切到 PostgreSQL 更容易出问题
- 数据一致性差

修复方案：
1. 在 schema 层区分“分类修正”和“文本修正”
2. 对分类字段强制转 int
3. 非法值返回 422

---

### 11. 文献导入去重逻辑过于脆弱

影响文件：
- server/src/api/publications.py

问题：
- 当前 duplicate 检查过于依赖 DOI
- 对无 DOI 数据的处理逻辑不够严谨

影响：
- 重复文献可能反复导入
- 数据质量变差

修复方案：
1. DOI 优先去重
2. 无 DOI 时退化为 title + authors + source 联合去重
3. 补充重复导入测试

---

### 12. 搜索接口返回结构不统一

影响文件：
- server/src/api/search.py
- web/src/pages/Library.tsx
- web/src/api/client.ts

问题：
- fulltext/hybrid 返回 `items: Article[]`
- semantic 返回 `items: [{ article, score }]`

影响：
- 前端处理分支变多
- 后续新增搜索模式容易出兼容问题

修复方案：
1. 统一返回结构
2. 推荐全部改成 `{ article, score?, mode }`
3. Library 页面只维护一种展示路径

---

## P2 级 BUG / 风险项

### 13. Skill 反馈评分语义和前端交互不一致

影响文件：
- server/src/api/schemas.py
- web/src/pages/ArticleDetail.tsx

问题：
- 后端 FeedbackCreate 允许 1-5 分
- 前端实际只有点赞/点踩

影响：
- 语义不统一
- 后续做统计或演进策略时口径混乱

修复方案：
1. 二选一：
   - 改成 `-1 / 1`
   - 或前端改成 1-5 评分
2. 保持数据库、API、前端三端统一

---

### 14. 搜索层和数据层缺少显式 response schema

影响文件：
- server/src/api/articles.py
- server/src/api/search.py
- server/src/api/publications.py

问题：
- 当前大量接口直接返回 ORM 对象
- 没有稳定的序列化边界

影响：
- 前后端对字段含义理解不一致
- 后续迁移和重构风险更高

修复方案：
1. 所有对前端暴露的接口都定义 response schema
2. 明确 list 和 detail 的返回形态
3. 把 JSON 字段、分类名、标签数组都在 API 层组装完成

---

## 建议修复顺序

### 阶段 1：先修核心运行链路

必须先修：
1. crawler.py 非法字段写入
2. video_processor.py 非法字段写入
3. KnowledgeEdge 导入和关系字段名不一致
4. 分类名称到 Category ID 的映射
5. 结构化字段 JSON 序列化

目标：
- 爬虫能稳定入库
- 上传能稳定生成文章
- 图谱边能正确写入

### 阶段 2：再修搜索和数据层

必须修：
1. FTS5 表和触发器
2. search.py 的返回结构统一
3. response schema 明确化

目标：
- 搜索结果真实可靠
- 前端不用猜字段结构

### 阶段 3：修前端对接和页面行为

必须修：
1. 图谱跳转路由错误
2. 分类树无数据来源
3. 文章卡片和详情页字段对不上

目标：
- 页面展示和交互完整可用

### 阶段 4：补测试

必须补：
- server/tests/test_api_articles.py
- server/tests/test_api_search.py
- server/tests/test_api_upload.py
- server/tests/test_api_graph.py
- server/tests/test_migrations.py

目标：
- 修一个问题，不引入新的问题

---

## 建议的实施原则

1. 先修后端数据契约，再修前端展示
2. 不要让前端去“猜测”后端字段含义
3. 不要继续返回 ORM 裸对象
4. 所有数组/对象字段统一 JSON 序列化策略
5. 所有需要给前端用的数据都通过 response schema 明确定义

---

## 验收清单

修完后至少验证以下场景：

1. 新建数据源 -> 手动触发采集 -> 文章成功入库
2. 上传 txt/pdf/mp3 -> 成功生成任务或文章
3. 搜索关键词 -> 全文搜索返回真实命中结果
4. 打开文章详情 -> 分类、标签、摘要显示正常
5. 打开知识图谱 -> 点击节点能跳转到详情页
6. Library 页面左侧分类树有数据并可筛选
7. 所有后端测试通过，前端至少能成功 build

---

## 下一步建议

如果继续由我执行，推荐按下面顺序直接开修：

1. 先修 P0：crawler.py、video_processor.py、processor.py、models.py
2. 再修 P0/P1：migrations + search.py
3. 再修 P1：articles API response schema + categories/tags API
4. 最后修前端：Library、ArticleDetail、ArticleCard、client.ts

这会是最稳妥、返工最少的一条路径。
