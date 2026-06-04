# AI 资讯合集平台 v2.0 Feature List

> 表头对齐标准：Mark | 〇级（领域）| 一级（模块）| 二级（能力）| 三级（功能）| 四级（子功能）| 描述 | 负责产品 | 必要性 | 涉及端 | 期望版本 | 说明 | 备注

| Mark | 〇级（领域） | 一级（模块） | 二级（能力） | 三级（功能） | 四级（子功能） | 描述 | 负责产品 | 必要性 | 涉及端 | 期望版本 | 说明 | 备注 |
|------|-------------|-------------|-------------|-------------|-------------|------|---------|--------|--------|---------|------|------|
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | 核心概念展示 | 概念卡片渲染 | 静态 HTML 渲染 9 个 AI Agent 核心概念卡片 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | 平台对比展示 | 五大阵营卡片 | 五个阵营卡片展示，含各平台工具描述 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | 垂直领域分析 | Data Agent 分析 | 四大阵营分析 + Top 5 对比表 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | 垂直领域分析 | Finance Agent 分析 | 四大阵营分析 + Top 5 对比表 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | 垂直领域分析 | Research Agent 分析 | 深度研究产品对比 + 全栈平台对比 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | Skills 指南 | Skills 全景展示 | 三大类别 Skills 卡片 + 原子化 TODO 方法论 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 竞品报告 | 静态报告展示 | Claude Code 指南 | 四种形态 + 配置说明 | Claude Code 配置指南与 2.1 更新内容 | Colin | Must | Web 端 | v1.0 | 已有功能 | |
| DONE | 前端展示 | 行业动态 | 静态外链展示 | 文字动态外链 | 外链卡片展示 | 3 个静态卡片链接到成都理工大学 AI 学习荟萃 | Colin | Must | Web 端 | v1.0 | 已有功能，v2 改为动态 | |
| DONE | 前端展示 | 行业动态 | 静态外链展示 | 视频周报外链 | B 站播放列表链接 | 2 个视频卡片链接到 B 站 GitHub/AI 周报播放列表 | Colin | Must | Web 端 | v1.0 | 已有功能，v2 保留 | |
| READY | 后端系统 | 基础设施 | 数据库设计 | 竞品报告存储 | report_sections 表 | 将原静态 HTML 章节内容迁移至 PostgreSQL JSONB 字段，支持后端动态渲染 | Colin | Must | 后端 | v2.0.0 | | 依赖 PostgreSQL |
| READY | 后端系统 | 基础设施 | 数据库设计 | 学术论文存储 | papers 表 | 存储爬取的论文元数据（标题/作者/摘要/链接/来源/日期），以 title+published_date 唯一去重 | Colin | Must | 后端 | v2.0.0 | | |
| READY | 后端系统 | 基础设施 | 数据库设计 | 行业动态存储 | news_items 表 | 存储爬取的行业资讯（来源/标题/摘要/链接/时间/分类），以 url 唯一去重 | Colin | Must | 后端 | v2.0.0 | | |
| READY | 后端系统 | 基础设施 | 数据库设计 | 用户数据存储 | users 表 | 存储用户注册信息（邮箱/密码哈希/昵称/注册时间） | Colin | Must | 后端 | v2.3.0 | | 密码 bcrypt 哈希 |
| READY | 后端系统 | 基础设施 | 数据库设计 | 用户收藏存储 | user_favorites 表 | 存储用户收藏关系（用户ID/条目类型/条目ID/收藏时间） | Colin | Must | 后端 | v2.3.0 | | |
| READY | 后端系统 | 基础设施 | 数据库设计 | 用户笔记存储 | user_notes 表 | 存储用户笔记（用户ID/条目类型/条目ID/笔记内容/创建更新时��） | Colin | Must | 后端 | v2.3.0 | | 最大 5000 字符 |
| READY | 后端系统 | 基础设施 | 缓存与队列 | Redis 缓存 | 热门数据缓存 | 缓存首页热门论文、最新动态等高频读数据，TTL 5 分钟 | Colin | Must | 后端 | v2.0.0 | | 依赖 Redis |
| READY | 后端系统 | 基础设施 | 定时任务 | 任务调度 | APScheduler 调度 | 配置各爬虫任务的 cron 表达式，管理任务启停，记录执行日志 | Colin | Must | 后端 | v2.0.0 | | 单机轻量方案 |
| READY | 后端系统 | API 服务 | 竞品报告接口 | 章节列表获取 | GET /api/report/sections | 返回全部章节列表（key/title/sort_order），供前端构建导航与页面 | Colin | Must | 后端 | v2.0.0 | | |
| READY | 后端系统 | API 服务 | 竞品报告接口 | 章节详情获取 | GET /api/report/sections/{key} | 返回单个章节完整内容（JSONB 解析为结构化数据） | Colin | Must | 后端 | v2.0.0 | | |
| READY | 后端系统 | API 服务 | 论文接口 | 论文列表获取 | GET /api/papers | 支持 source/category/keyword/date_from/date_to/page/size 参数筛选，返回分页结果 | Colin | Must | 后端 | v2.1.0 | | |
| READY | 后端系统 | API 服务 | 论文接口 | 论文详情获取 | GET /api/papers/{id} | 返回单篇论文完整元数据 | Colin | Must | 后端 | v2.1.0 | | |
| READY | 后端系统 | API 服务 | 论文接口 | 论文统计获取 | GET /api/papers/stats | 返回按来源/月份分布的论文数量统计 | Colin | Nice to have | 后端 | v2.1.0 | | 用于统计图表 |
| READY | 后端系统 | API 服务 | 动态接口 | 动态列表获取 | GET /api/news | 支持 category/date/page/size 参数筛选，返回分页结果 | Colin | Must | 后端 | v2.2.0 | | |
| READY | 后端系统 | API 服务 | 动态接口 | 动态详情获取 | GET /api/news/{id} | 返回单条动态完整信息 | Colin | Nice to have | 后端 | v2.2.0 | | |
| READY | 后端系统 | API 服务 | 用户接口 | 用户注册 | POST /api/user/register | 接收邮箱/密码/昵称，校验重复邮箱，返回 JWT Token | Colin | Must | 后端 | v2.3.0 | | |
| READY | 后端系统 | API 服务 | 用户接口 | 用户登录 | POST /api/user/login | 校验邮箱/密码，返回 JWT Token（7天有效） | Colin | Must | 后端 | v2.3.0 | | |
| READY | 后端系统 | API 服务 | 用户接口 | 用户信息获取 | GET /api/user/me | 根据 JWT Token 返回当前用户信息 | Colin | Must | 后端 | v2.3.0 | | |
| READY | 后端系统 | API 服务 | 用户接口 | 添加收藏 | POST /api/user/favorites | 接收 item_type 和 item_id，写入收藏记录 | Colin | Must | 后端 | v2.3.0 | | 需登录校验 |
| READY | 后端系统 | API 服务 | 用户接口 | 取消收藏 | DELETE /api/user/favorites/{id} | 删除指定收藏记录 | Colin | Must | 后端 | v2.3.0 | | 校验用户归属 |
| READY | 后端系统 | API 服务 | 用户接口 | 收藏列表 | GET /api/user/favorites | 返回当前用户收藏列表，支持 item_type 筛选 | Colin | Must | 后端 | v2.3.0 | | 按收藏时间倒序 |
| READY | 后端系统 | API 服务 | 用户接口 | 添加/更新笔记 | POST /api/user/notes | 接收 item_type/item_id/content，存在则更新，不存在则新建 | Colin | Must | 后端 | v2.3.0 | | upsert 逻辑 |
| READY | 后端系统 | API 服务 | 用户接口 | 删除笔记 | DELETE /api/user/notes/{id} | 删除指定笔记记录 | Colin | Must | 后端 | v2.3.0 | | 校验用户归属 |
| READY | 后端系统 | API 服务 | 用户接口 | 笔记列表 | GET /api/user/notes | 返回当前用户笔记列表 | Colin | Must | 后端 | v2.3.0 | | 按更新时间倒序 |
| READY | 内容采集 | 学术爬虫 | arXiv 论文爬取 | 定时爬取 | arXiv API 调用 | 每日 08:00 调用 arXiv API，获取 cs.AI/cs.CL/cs.LG/stat.ML 分类前一日论文 | Colin | Must | 后端 | v2.1.0 | | 依赖 arXiv API |
| READY | 内容采集 | 学术爬虫 | arXiv 论文爬取 | 数据解析 | API 响应解析 | 解析 Atom XML 响应，提取标题/作者/摘要/链接/PDF/日期/分类 | Colin | Must | 后端 | v2.1.0 | | |
| READY | 内容采集 | 学术爬虫 | NeurIPS 论文爬取 | 定时爬取 | Proceedings 页面爬取 | 每周一 09:00 爬取 NeurIPS Proceedings 页面，获取最新会议论文 | Colin | Must | 后端 | v2.1.0 | | 依赖 papers.nips.cc |
| READY | 内容采集 | 学术爬虫 | ICLR 论文爬取 | 定时爬取 | OpenReview API 调用 | 每周一 10:00 调用 OpenReview API，获取最新 ICLR 论文 | Colin | Must | 后端 | v2.1.0 | | 依赖 OpenReview API |
| READY | 内容采集 | 学术爬虫 | ICML 论文爬取 | 定时爬取 | PMLR 页面爬取 | 获取 ICML 会议论文元数据 | Colin | Nice to have | 后端 | v2.1.0 | | 依赖 PMLR |
| READY | 内容采集 | 学术爬虫 | ACL 论文爬取 | 定时爬取 | ACL Anthology 页面爬取 | 获取 ACL 会议论文元数据 | Colin | Nice to have | 后端 | v2.1.0 | | 依赖 ACL Anthology |
| READY | 内容采集 | 学术爬虫 | 通用爬虫能力 | 去重机制 | URL 重复检查 | 以 title+published_date 为唯一键，插入时使用 INSERT ON CONFLICT DO NOTHING | Colin | Must | 后端 | v2.1.0 | | |
| READY | 内容采集 | 学术爬虫 | 通用爬虫能力 | 失败重试 | 3 次重试机制 | 单次爬取失败后等待 30 分钟重试，最多 3 次，仍失败则记录告警日志并跳过 | Colin | Must | 后端 | v2.1.0 | | |
| READY | 内容采集 | 学术爬虫 | 通用爬虫能力 | 频率限制 | 请求间隔控制 | 同一源两次请求间隔 ≥ 3 秒，避免触发反爬 | Colin | Must | 后端 | v2.1.0 | | |
| READY | 内容采集 | 资讯爬虫 | 中文源爬取 | RSS 解析 | 中文 RSS 源定时抓取 | 每 3 小时抓取机器之心/量子位/新智元的 RSS 订阅，解析标准 RSS 2.0 XML | Colin | Must | 后端 | v2.2.0 | | 依赖各源 RSS 服务 |
| READY | 内容采集 | 资讯爬虫 | 英文源爬取 | RSS 解析 | 英文 RSS 源定时抓取 | 每 6 小时抓取 MIT Tech Review/Ars Technica/The Verge AI 板块 RSS | Colin | Must | 后端 | v2.2.0 | | 依赖各源 RSS 服务 |
| READY | 内容采集 | 资讯爬虫 | 通用爬虫能力 | 去重与重试 | 同论文爬虫 | 以 url 为唯一键去重，失败重试逻辑同学术爬虫 | Colin | Must | 后端 | v2.2.0 | | |
| READY | 前端展示 | 首页重构 | 动态首页 | 今日快讯 | 24h 热门动态展示 | 首页 Hero 下方展示最近 24 小时爬取的前 5 条动态 | Colin | Must | Web 端 | v2.4.0 | | 数据来源 /api/news |
| READY | 前端展示 | 首页重构 | 动态首页 | 热门论文 | 7 天热门论文展示 | 展示最近 7 天收藏数最多的前 6 篇论文 | Colin | Must | Web 端 | v2.4.0 | | 需用户收藏数据 |
| READY | 前端展示 | 首页重构 | 动态首页 | 报告速览 | 竞品报告导航卡片 | 4 个卡片引导进入核心概念/平台对比/垂直领域/Skills 指南 | Colin | Must | Web 端 | v2.4.0 | | |
| READY | 前端展示 | 学术板块 | 论文列表页 | 列表展示 | 论文卡片列表 | 按筛选条件展示论文卡片（标题/作者/来源标���/摘要/日期），每页 20 条，底部分页器 | Colin | Must | Web 端 | v2.1.0 | | |
| READY | 前端展示 | 学术板块 | 论文列表页 | 顶部筛选栏 | 来源/关键词/日期/排序 | 多选顶刊来源、关键词输入框、起止日期选择器、排序方式选择 | Colin | Must | Web 端 | v2.1.0 | | |
| READY | 前端展示 | 学术板块 | 论文列表页 | 收藏操作 | 收藏按钮 | 每条论文卡片标题旁有收藏图标，已登录用户可收藏/取消 | Colin | Must | Web 端 | v2.3.0 | | 未登录点击时提示 |
| READY | 前端展示 | 学术板块 | 论文列表页 | 空状态与加载 | 骨架屏 / 空状态 / 错误重试 | 加载中显示骨架屏，无数据时显示空状态提示，出错时显示重试按钮 | Colin | Must | Web 端 | v2.1.0 | | |
| READY | 前端展示 | 学术板块 | 论文详情页 | 详情展示 | 完整论文信息 | 展示完整标题/全部作者/来源/日期/摘要全文/PDF链接 | Colin | Must | Web 端 | v2.1.0 | | |
| READY | 前端展示 | 学术板块 | 论文详情页 | 操作按钮 | 查看原文/下载PDF/收藏/笔记 | 底部操作区：新标签页打开原文/PDF，已登录可收藏与添加笔记 | Colin | Must | Web 端 | v2.1.0 | | |
| READY | 前端展示 | 学术板块 | 论文详情页 | 笔记编辑 | 笔记文本区 | 多行文本输入，最大 5000 字符，实时字符计数，保存按钮 | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | 行业动态 | 动态列表页 | 列表展示 | 动态卡片列表 | 按筛选条件展示动态卡片（来源/标题/摘要/时间/标签），每页 20 条 | Colin | Must | Web 端 | v2.2.0 | | |
| READY | 前端展示 | 行业动态 | 动态列表页 | 顶部筛选栏 | 分类/时间/搜索 | 多选分类、时间范围单选、搜索框 | Colin | Must | Web 端 | v2.2.0 | | |
| READY | 前端展示 | 行业动态 | 动态列表页 | 相对时间显示 | 发布时间人性化 | 24 小时内显示"X 小时前"，超过 24 小时显示绝对日期 | Colin | Must | Web 端 | v2.2.0 | | |
| READY | 前端展示 | 用户系统 | 注册页面 | 注册表单 | 昵称/邮箱/密码/确认密码 | 各字段独立校验，失焦触发，全部通过后可提交，成功后自动登录跳转首页 | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | 用户系统 | 登录页面 | 登录表单 | 邮箱/密码 | 提交后校验，成功后跳转上一页或首页，JWT Token 存储 localStorage | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | 用户系统 | 导航栏用户区域 | 登录态切换 | 未登录/已登录状态 | 未登录显示注册/登录按钮，已登录显示昵称+下拉菜单（收藏/笔记/退出） | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | 用户系统 | 我的收藏页 | 收藏列表管理 | 论文/动态 Tab 切换 | 按类型 Tab 切换，每条可点击跳详情或取消收藏，取消前弹窗确认 | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | 用户系统 | 我的笔记页 | 笔记列表管理 | 笔记卡片列表 | 展示关���标题/笔记摘要/更新时间，可编辑或删除，删除前弹窗确认 | Colin | Must | Web 端 | v2.3.0 | | |
| READY | 前端展示 | UI 优化 | 导航栏优化 | 导航项精简 | 4 项主导航 | 首页/竞品报告/学术板块/行业动态，当前页高亮 | Colin | Must | Web 端 | v2.4.0 | | |
| READY | 前端展示 | UI 优化 | 移动端适配 | 响应式布局 | 三档断点适配 | 768px 平板两列/480px 手机单列，汉堡菜单，表格横向滚动 | Colin | Must | Web 端 | v2.4.0 | | |
| READY | 前端展示 | UI 优化 | 暗色模式 | 主题切换 | 浅色/暗色切换 | 导航栏切换按钮，跟随系统偏好，localStorage 记忆 | Colin | Nice to have | Web 端 | v2.4.0 | | |
| READY | 前端展示 | UI 优化 | 内容动态化 | 静态内容迁移 | 报告内容数据库存储 | 原 HTML 静态文本迁移至 report_sections 表，Jinja2 模板渲染 | Colin | Must | 全栈 | v2.0.0 | | v2.0 关键任务 |
| READY | 前端展示 | UI 优化 | 后台管理 | 内容编辑 | Markdown 编辑器 | 后台管理页面提供 Markdown 编辑器编辑竞品报告各章节 | Colin | Nice to have | Web 端 | v2.4.0 | | 简单实现 |
| READY | 前端展示 | UI 优化 | 数据看板 | 更新日志页 | 数据源状态展示 | 展示各数据源最近更新时间与收录条目数 | Colin | Nice to have | Web 端 | v2.4.0 | | |
