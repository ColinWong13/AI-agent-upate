# AI 资讯合集平台 v2.0 时间线与版本管理

---

## 1. 里程碑总览

```
v1.0 (已完成)          v2.0.0          v2.1.0         v2.2.0         v2.3.0         v2.4.0         v2.5.0
静态 HTML            后端+数据库      学术论文板块    行业动态爬取    用户系统       UI优化         联调上线
  │                    │               │              │              │             │              │
  └── 4月20日          └── W1-W2       └── W3-W4      └── W5-W6      └── W7-W8     └── W9         └── W10
```

---

## 2. 版本详细排期

### v2.0.0 — 后端系统搭建 + 数据库（2 周 | W1-W2）

| 日期 | 任务 | 产出 |
|------|------|------|
| W1-D1 | 项目骨架搭建 | FastAPI 项目初始化，目录结构，requirements.txt |
| W1-D2 | 数据库设计 | 6 张核心表 DDL，SQLAlchemy 模型定义 |
| W1-D3 | Redis 集成 | 缓存工具类，连接池配置 |
| W1-D4 | 竞品报告 API | GET /api/report/sections，/sections/{key} |
| W1-D5 | 数据迁移脚本 | 将 index.html 静态内容解析写入 report_sections 表 |
| W2-D1 | Jinja2 模板拆分 | base.html / index.html / report.html 拆分 |
| W2-D2 | 首页动态渲染 | Hero + 章节导航从数据库加载 |
| W2-D3 | 竞品报告页动态渲染 | 全部章节从数据库渲染 |
| W2-D4 | Docker 配置 | Dockerfile + docker-compose.yml（FastAPI + PostgreSQL + Redis） |
| W2-D5 | 自测 + 代码清理 | 确保 v2.0.0 可独立部署运行 |

### v2.1.0 — 学术论文板块（2 周 | W3-W4）

| 日期 | 任务 | 产出 |
|------|------|------|
| W3-D1 | arXiv 爬虫 | arxiv.py，调用 arXiv API，解析 Atom XML |
| W3-D2 | NeurIPS + ICLR 爬虫 | neurIPS.py / iclr.py |
| W3-D3 | ICML + ACL 爬虫（Nice to have） | icml.py / acl.py |
| W3-D4 | APScheduler 集成 | scheduler.py，cron 配置，启停控制 |
| W3-D5 | 论文 API | GET /api/papers（分页/筛选），/api/papers/{id}，/api/papers/stats |
| W4-D1 | 论文列表页模板 | papers.html，筛选栏 + 卡片列表 + 分页器 |
| W4-D2 | 论文详情页模板 | paper_detail.html，完整信息 + 操作按钮 |
| W4-D3 | 骨架屏 + 空状态 + 错误重试 | 前端状态覆盖 |
| W4-D4 | 联调自测 | 爬虫 → API → 前端全链路验证 |
| W4-D5 | buffer | 修 bug，补充边界处理 |

### v2.2.0 — 行业动态自动爬取（1.5 周 | W5-W6.5）

| 日期 | 任务 | 产出 |
|------|------|------|
| W5-D1 | 中文 RSS 爬虫 | 机器之心 / 量子位 / 新智元 RSS 解析 |
| W5-D2 | 英文 RSS 爬虫 | MIT Tech Review / Ars Technica / The Verge AI |
| W5-D3 | 动态 API | GET /api/news（分页/筛选），/api/news/{id} |
| W5-D4 | 动态列表页模板 | news.html，筛选栏 + 卡片列表 + 分页 |
| W5-D5 | 相对时间 + 分类标签 | 前端时间格式化，tag 渲染 |
| W6-D1 | 联调自测 | 爬虫 → API → 前端 |
| W6-D2 | buffer | |
| W6-D3 | buffer | |

### v2.3.0 — 用户系统（1.5 周 | W6.5-W8）

| 日期 | 任务 | 产出 |
|------|------|------|
| W6-D4 | 用户注册 API | POST /api/user/register + 字段校验 |
| W6-D5 | 用户登录 API | POST /api/user/login + JWT 签发 |
| W7-D1 | JWT 中间件 | 依赖注入，Token 校验，过期处理 |
| W7-D2 | 收藏 API | POST/DELETE/GET favorites |
| W7-D3 | 笔记 API | POST/DELETE/GET notes |
| W7-D4 | 注册/登录页模板 | register.html / login.html + 表单校验 |
| W7-D5 | 导航栏用户区域 | 登录态切换，下拉菜单 |
| W8-D1 | 我的收藏页模板 | favorites.html，Tab 切换 |
| W8-D2 | 我的笔记页模板 | notes.html，编辑/删除 |
| W8-D3 | 联调自测 + buffer | |

### v2.4.0 — UI 优化（1 周 | W9）

| 日期 | 任务 | 产出 |
|------|------|------|
| W9-D1 | 首页重构 | 今日快讯 / 热门论文 / 报告速览 |
| W9-D2 | 响应式适配 | 三档断点 CSS，汉堡菜单，表格滚动 |
| W9-D3 | 暗色模式 | CSS 变量切换，localStorage 持久化 |
| W9-D4 | 后台管理页（简易版） | 内容编辑 Markdown 编辑器 |
| W9-D5 | 数据更新日志页 | 数据源状态面板 |

### v2.5.0 — 联调测试上线（1 周 | W10）

| 日期 | 任务 | 产出 |
|------|------|------|
| W10-D1 | 全链路集成测试 | 执行 TestCases_v2.0.md 中所有用例 |
| W10-D2 | Bug 修复 | 按 P0 → P1 → P2 优先级修复 |
| W10-D3 | 性能测试 | 接口响应时间、并发测试 |
| W10-D4 | 部署文档 | README.md，部署步骤 |
| W10-D5 | 上线 | 部署到服务器，正式对外 |

---

## 3. 分支管理

```
main ──────────────────────────────────────────────────────────── ● v2.5.0
  │                                                                 │
  └── develop ──────────────────────────────────────────────────────┤
        │                                                           │
        ├── feature/v2.0.0-backend ────── ● ── PR ── ──┤
        ├── feature/v2.1.0-papers ─────── ● ── PR ── ──┤
        ├── feature/v2.2.0-news-crawler ─ ● ── PR ── ──┤
        ├── feature/v2.3.0-user-system ── ● ── PR ── ──┤
        ├── feature/v2.4.0-ui-optimize ── ● ── PR ── ──┤
        └── feature/v2.5.0-test-release ─ ● ── PR ── ──┘
```

**规则**：
- `main`：生产分支，仅通过 PR 从 develop 合并，禁止直接推送。
- `develop`：开发主线，所有 feature 分支从此切出并合并回来。
- `feature/vX.X.X-xxx`：每个版本一个功能分支。
- `hotfix/xxx`：线上紧急修复，从 main 切出，修复后合并回 main 和 develop。

---

## 4. 提交规范

```
<type>: <简短描述>

类型取值：
  feat     - 新功能
  fix      - Bug 修复
  refactor - 重构（不改变功能）
  docs     - 文档
  test     - 测试
  chore    - 工程配置 / 依赖更新

示例：
  feat: add arXiv paper crawler with dedup
  fix: handle empty RSS response without crash
  docs: add API usage examples to README
  test: add user registration validation tests
```

---

## 5. 风险与应对

| 风险 | 影响 | 概率 | 应对 |
|------|------|------|------|
| arXiv API 限流或变更 | 爬取失败 | 中 | 配置 User-Agent，遵守速率限制，准备 Fallback 数据 |
| 国内 RSS 源不稳定 | 中文资讯缺失 | 高 | 多源冗余（至少 3 个中文源），单源失败不影响整体 |
| 反爬策略升级 | 爬虫失效 | 中 | 请求频率控制 ≥3s 间隔，使用标准 User-Agent |
| 单人开发进度延误 | 排期延后 | 中 | 按优先级裁剪，Nice to have 功能可延后至 v2.6+ |
| 服务器成本 | 超出预算 | 低 | 初期单机部署（2C4G 即可），日爬取量预估 < 500 条 |

---

## 6. 总工期

| 阶段 | 时长 | 累计 |
|------|------|------|
| v2.0.0 后端搭建 | 2 周 | 2 周 |
| v2.1.0 学术板块 | 2 周 | 4 周 |
| v2.2.0 行业动态 | 1.5 周 | 5.5 周 |
| v2.3.0 用户系统 | 1.5 周 | 7 周 |
| v2.4.0 UI 优化 | 1 周 | 8 周 |
| v2.5.0 联调上线 | 1 周 | **9 周** |

**预计完成日期**：2026 年 7 月中旬（从 5 月 7 日起算 9 周，含合理 buffer）。
