# 项目开发计划 v2.5.0

## Context
在现有 AI Agent 竞品调研平台基础上，增强论文/行业动态的数据采集、筛选和智能摘要能力。当前平台只有基础的来源筛选和定时爬虫，缺少用户自定义筛选、手动触发爬虫、以及 AI 驱动的周报摘要功能。

## 实施概览

| # | 功能 | 复杂度 | 依赖 |
|---|------|--------|------|
| 1 | 论文筛选增强（日期范围、顶刊多选） | 低 | 无 |
| 2 | 手动触发爬虫按钮 | 低 | 无 |
| 3 | 论文周报告示板 + LLM 摘要 | 高 | 需先建基础设施 |
| 4 | 行业动态周报告示板 + 新闻爬虫 | 高 | 依赖 #3 基础设施 |
| 5 | 删除报告页"七、行业动态"章节 | 低 | 无 |

---

## Phase 1: 基础设施（共享模块）

### 1.1 新建 `backend/models/system_config.py`
- key-value 配置表，主键 `key`(String)，`value`(Text)
- 用于存储 LLM 配置（provider/base_url/model/api_key）
- 注册到 `backend/models/__init__.py`

### 1.2 新建 `backend/models/weekly_digest.py`
- 周报摘要表：`id`, `digest_type`(paper/news), `title`, `content`(HTML), `week_start`, `week_end`, `created_at`, `is_latest`
- 注册到 `backend/models/__init__.py`

### 1.3 新建 `backend/services/` 包
- `backend/services/__init__.py`
- `backend/services/llm.py` — LLM 调用抽象层
  - 默认使用 Ollama (`http://localhost:11434`, `qwen2.5:7b`)，免费开源
  - 支持 OpenAI 兼容 API（用户可在管理页配置）
  - 配置优先级：DB SystemConfig > 环境变量 > 硬编码默认值
  - `get_llm_config()` / `call_llm(prompt, system_prompt)` 两个核心函数
- `backend/services/digest.py` — 周报生成逻辑
  - `generate_paper_digest()` — 拉取近7天论文 → LLM 摘要 → 存入 DB
  - `generate_news_digest()` — 拉取近7天新闻 → LLM 摘要 → 存入 DB
  - 两个函数均包含 LLM 调用失败的优雅降级处理

### 1.4 更新 `backend/config.py`
- 新增环境变量：`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`

### 1.5 新建 `backend/routers/digest.py`
- `GET /api/digest/{type}` — 获取指定类型所有周报
- `GET /api/digest/{type}/latest` — 获取最新周报
- `POST /api/digest/{type}/generate` — 手动触发生成
- `GET /api/digest/config/llm` — 获取 LLM 配置
- `PUT /api/digest/config/llm` — 更新 LLM 配置
- 注册到 `backend/main.py`

---

## Phase 2: 功能 #5 — 删除报告页行业动态章节（先做，无依赖）

### 修改 `backend/migrate.py`
- 从 `SECTION_META` 中删除 `"news": {"title": "七、行业动态", "sort_order": 7}`
- 新增 `cleanup_news_section()` 函数，删除 DB 中 `section_key='news'` 的记录
- `index.html` 动态遍历 sections，无需修改

---

## Phase 3: 功能 #1 — 论文筛选增强

### 3.1 修改 `backend/main.py` — `page_papers` 路由
- 新增 `date_from` / `date_to` 查询参数 (str, YYYY-MM-DD)
- 新增 `sources` 查询参数 (逗号分隔的多选)
- 保留原有 `source` 参数向下兼容
- 将新参数传入模板上下文和分页链接

### 3.2 修改 `backend/templates/papers.html`
- 将单一下拉框替换为顶刊复选框组（arxiv/neurips/iclr/icml/acl/cvpr）
- 新增日期范围选择器 (input[type=date])
- 保留关键词搜索框
- 新增"清除筛选"按钮
- 分页链接携带所有筛选参数

### 3.3 修改 `backend/static/style.css`
- 新增 `.venue-group`、`input[type="date"]` 等样式

---

## Phase 4: 功能 #2 — 手动触发爬虫

### 4.1 修改 `backend/routers/paper.py`
- 新增 `POST /api/papers/crawl` 端点
- 使用 `asyncio.gather` 并发执行全部 6 个爬虫
- 返回聚合结果（每个爬虫的 fetched/saved 数量）

### 4.2 修改 `backend/templates/papers.html`
- 在筛选区域上方添加"立即爬取"按钮
- JS 调用 `/api/papers/crawl`，显示进度，完成后自动刷新

### 4.3 修改 `backend/templates/admin.html`
- 同样添加爬虫触发按钮（管理页也可触发）

---

## Phase 5: 功能 #3 — 论文周报告示板

### 5.1 修改 `backend/scheduler.py`
- 新增定时任务：每周日 20:00 执行 `generate_paper_digest()`

### 5.2 修改 `backend/main.py` — `page_papers` 路由
- 查询最新 `digest_type='paper'` 的 WeeklyDigest
- 查询往期 paper digests（is_latest=False）
- 传入模板

### 5.3 修改 `backend/templates/papers.html`
- 在 hero 下方、筛选表单上方插入本周告示板
- 告示板样式：边框 + 浅色背景，显示 LLM 生成的 HTML 内容
- 往期周报用 `<details>` 折叠，点击展开查看

### 5.4 修改 `backend/templates/admin.html`
- 新增 LLM 配置区域（Provider 选择、API URL、Model、API Key）
- 页面加载时从 `/api/digest/config/llm` 获取当前配置并填充表单
- 保存时调用 `PUT /api/digest/config/llm`

---

## Phase 6: 功能 #4 — 行业动态周报告示板

### 6.1 新建 `backend/crawlers/news_crawler.py`
- 从 RSS 源自动抓取 AI 行业新闻（Hugging Face Daily Papers 等）
- 使用已有的 `feedparser` 库
- 存入 `NewsItem` 表（URL 去重）
- 暴露 `async crawl()` 函数

### 6.2 修改 `backend/scheduler.py`
- 新增新闻爬虫定时任务（每6小时）
- 新增新闻周报生成定时任务（每周日 20:30）

### 6.3 修改 `backend/routers/news.py`
- 新增 `POST /api/news/crawl` — 手动触发新闻爬虫

### 6.4 修改 `backend/main.py` — `page_news` 路由
- 查询最新/往期 `digest_type='news'` 的 WeeklyDigest
- 传入模板

### 6.5 修改 `backend/templates/news.html`
- 在分类筛选栏上方插入周报告示板
- 与论文页相同的告示板 + 折叠往期模式

---

## 关键文件清单

| 操作 | 文件路径 |
|------|---------|
| 新建 | `backend/models/system_config.py` |
| 新建 | `backend/models/weekly_digest.py` |
| 新建 | `backend/services/__init__.py` |
| 新建 | `backend/services/llm.py` |
| 新建 | `backend/services/digest.py` |
| 新建 | `backend/routers/digest.py` |
| 新建 | `backend/crawlers/news_crawler.py` |
| 修改 | `backend/models/__init__.py` |
| 修改 | `backend/config.py` |
| 修改 | `backend/main.py` |
| 修改 | `backend/scheduler.py` |
| 修改 | `backend/migrate.py` |
| 修改 | `backend/routers/paper.py` |
| 修改 | `backend/routers/news.py` |
| 修改 | `backend/templates/papers.html` |
| 修改 | `backend/templates/news.html` |
| 修改 | `backend/templates/admin.html` |
| 修改 | `backend/static/style.css` |

---

## 验证方案

1. **功能 #5**：运行 `python migrate.py`，确认 DB 中 `section_key='news'` 记录已删除，访问 `/report` 页面确认无行业动态章节
2. **功能 #1**：访问 `/papers`，测试日期范围筛选、顶刊复选框多选、关键词搜索，验证分页链接保留所有参数
3. **功能 #2**：点击"立即爬取"按钮，确认返回 fetched/saved 数量，页面刷新后显示新数据
4. **功能 #3**：
   - 手动调用 `POST /api/digest/paper/generate`，确认 DB 中有新记录
   - 访问 `/papers`，确认告示板显示本周摘要
   - 点击"往期周报"折叠面板，确认可展开查看
5. **功能 #4**：
   - 手动调用 `POST /api/news/crawl`，确认新闻爬虫正常工作
   - 手动调用 `POST /api/digest/news/generate`，确认新闻周报生成
   - 访问 `/news`，确认告示板正常显示
6. **管理页 LLM 配置**：修改 LLM 配置并保存，调用 `/api/digest/config/llm` 确认配置已更新
7. **整体回归**：启动 `uvicorn main:app`，访问所有页面确认无报错
