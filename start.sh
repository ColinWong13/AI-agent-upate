#!/bin/bash
# The Agent Report — 一键启动脚本
set -e
cd "$(dirname "$0")/backend"

# 1. 停止旧进程
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 2. 启动服务（保留已有数据库）
USE_SQLITE=true uvicorn main:app --host 127.0.0.1 --port 8000 &
sleep 2

# 3. 首次启动时导入竞品报告数据（只跑一次）
USE_SQLITE=true python3 -c "
from database import AsyncSessionLocal
from sqlalchemy import select, func
from models.report import ReportSection
import asyncio
async def check():
    async with AsyncSessionLocal() as db:
        count = (await db.execute(select(func.count(ReportSection.id)))).scalar()
        if count == 0:
            print('First run: importing report data...')
asyncio.run(check())
" 2>&1 | grep -q "First run" && USE_SQLITE=true python3 migrate.py || echo "Report data already loaded."

# 4. 启动时立即爬一次 arXiv（如果有网络）
echo "Fetching latest papers from arXiv..."
USE_SQLITE=true python3 -c "
import asyncio, logging
logging.basicConfig(level=logging.WARNING)
from crawlers.arxiv import crawl
try:
    result = asyncio.run(crawl())
    print(f'Papers: {result[\"fetched\"]} fetched, {result[\"saved\"]} new')
except Exception as e:
    print(f'arXiv crawl skipped: {e}')
" 2>&1 || echo "arXiv crawl skipped (network unavailable)"

# 5. 验证 & 打开浏览器
curl -s http://127.0.0.1:8000/api/health
echo ""
echo "The Agent Report is live at http://127.0.0.1:8000"
open http://127.0.0.1:8000/
