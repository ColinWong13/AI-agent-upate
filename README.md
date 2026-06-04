# The Agent Report

AI 行业情报聚合平台，自动追踪学术论文、行业动态与竞品报告，并生成中文 AI 摘要。

## 功能

- **学术论文** — 追踪 arXiv、NeurIPS、ICLR、ICML、ACL、CVPR 最新论文，支持按来源 / 日期 / 关键词筛选
- **行业动态** — 聚合 36氪、量子位等中文 AI 资讯，RSS 自动更新
- **竞品报告** — 结构化竞品分析与行业趋势报告
- **AI 周报** — 每周自动生成论文摘要 + 行业动态总结（需 LLM）
- **用户系统** — 注册 / 登录 / 收藏 / 个人笔记

## 快速开始

### 环境要求

- **Python 3.11+**
- **Ollama**（可选，用于 AI 摘要生成）— [安装指南](https://ollama.com)

### 一键启动（推荐）

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <repo>
./start.sh
```

脚本会自动：
1. 使用 SQLite 启动服务（无需安装数据库）
2. 导入竞品报告数据
3. 爬取一次 arXiv 论文
4. 打开浏览器访问 `http://127.0.0.1:8000`

### 启用 AI 摘要（可选但推荐）

1. 安装 Ollama 并拉取模型：
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 拉取推荐模型（约 4.7GB）
ollama pull qwen2.5:7b
```

2. 确保 Ollama 在后台运行，服务会自动检测并调用。

如需使用其他模型或 OpenAI 兼容 API，配置环境变量：
```bash
export LLM_PROVIDER=openai
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4o-mini
export LLM_API_KEY=sk-xxx
```

### Docker 部署

```bash
docker compose up -d
```

这会启动三个服务：
- **app** — Web 服务 (`:8000`)
- **db** — PostgreSQL 15
- **redis** — Redis 7

Docker 默认使用 SQLite。如需切换 PostgreSQL，设置环境变量：
```bash
USE_SQLITE=false docker compose up -d
```

## 配置

复制环境变量模板并修改：

```bash
cp .env.example .env
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `USE_SQLITE` | `true` | 使用 SQLite（无需额外数据库） |
| `DATABASE_URL` | `sqlite+aiosqlite:///./ai_agent.db` | 数据库连接（SQLite 模式） |
| `DATABASE_URL_SYNC` | `sqlite:///./ai_agent.db` | 同步数据库连接 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接（可选） |
| `JWT_SECRET` | `dev-secret-change-in-production` | JWT 签名密钥 |
| `LLM_PROVIDER` | `ollama` | LLM 类型：`ollama` 或 `openai` |
| `LLM_BASE_URL` | `http://localhost:11434` | LLM API 地址 |
| `LLM_MODEL` | `qwen2.5:7b` | 模型名称 |
| `LLM_API_KEY` | — | API 密钥（Ollama 不需要） |
| `CRAWL_INTERVAL_HOURS` | `6` | 新闻爬取间隔 |

## 项目结构

```
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── docs/                     # 产品需求 & 设计文档
│   ├── PRD_v2.0.md
│   ├── PRD_v2.5.0.md
│   ├── FeatureList_v2.0.md
│   ├── TestCases_v2.0.md
│   └── Timeline_v2.0.md
└── backend/                  # 应用代码
    ├── main.py               # FastAPI 入口 & 页面路由
    ├── config.py             # 配置管理
    ├── database.py           # 数据库连接 & 自动建表
    ├── auth.py               # JWT 认证
    ├── scheduler.py          # 定时任务（爬虫 & 周报）
    ├── migrate.py            # 数据迁移 / 初始化
    ├── routers/              # API 路由
    ├── crawlers/             # 爬虫（arXiv / NeurIPS / ICLR / ICML / ACL / CVPR / 新闻）
    ├── services/             # 业务逻辑（AI 周报 / LLM 调用）
    ├── models/               # SQLAlchemy 数据模型
    ├── templates/            # Jinja2 页面模板
    └── static/               # CSS 等静态资源
```

## License

[MIT](LICENSE)

## 技术栈

- **后端**: FastAPI (Python) + SQLAlchemy + Jinja2
- **数据库**: SQLite（默认）/ PostgreSQL
- **缓存**: Redis（可选）
- **任务调度**: APScheduler
- **AI**: Ollama / OpenAI 兼容 API
- **前端**: 服务端渲染，Newspaper 风格设计

## License

MIT
