import logging
from datetime import date, timedelta
from sqlalchemy import select, update
from database import AsyncSessionLocal
from models.paper import Paper
from models.news import NewsItem
from models.weekly_digest import WeeklyDigest
from services.llm import call_llm

logger = logging.getLogger(__name__)

PAPER_SYSTEM_PROMPT = "你是一个专业的AI学术研究助手。请用中文回复，使用HTML格式（h3, p, ul, li标签），保持简洁，不超过500字。"

PAPER_SUMMARY_PROMPT = """请根据以下过去一周发表的重要学术论文列表，生成一份简洁的中文周报摘要。摘要应包括：
1. 本周主要研究方向（2-3个方向）
2. 每个方向的代表性论文（最多3篇，包含标题和关键发现）
3. 总体趋势观察

论文列表：
"""

NEWS_SYSTEM_PROMPT = "你是一个专业的AI行业分析师。请用中文回复，使用HTML格式（h3, p, ul, li标签），保持简洁，不超过500字。"

NEWS_SUMMARY_PROMPT = """请根据以下过去一周的AI行业新闻，生成一份简洁的中文周报摘要。摘要应包括：
1. 本周重大事件（2-3件）
2. 行业趋势分析
3. 值得关注的公司/产品动态

新闻列表：
"""


async def generate_paper_digest() -> dict | None:
    week_end = date.today()
    week_start = week_end - timedelta(days=7)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Paper)
            .where(Paper.published_date >= week_start, Paper.published_date <= week_end)
            .order_by(Paper.published_date.desc())
            .limit(100)
        )
        papers = result.scalars().all()

        if not papers:
            logger.info("No papers found for weekly digest")
            return None

        paper_texts = []
        for p in papers:
            author_str = ", ".join(p.authors[:3]) if p.authors else "Unknown"
            paper_texts.append(f"- [{p.source.upper()}] {p.title} ({author_str})")
        prompt = PAPER_SUMMARY_PROMPT + "\n".join(paper_texts)

        try:
            content = await call_llm(prompt, PAPER_SYSTEM_PROMPT)
        except Exception as e:
            logger.error(f"LLM call failed for paper digest: {e}")
            content = f"<p>本周共收录 {len(papers)} 篇论文，涵盖 {', '.join(sorted(set(p.source for p in papers)))} 等来源。LLM 摘要生成失败：{e}</p><p>请检查 LLM 配置或稍后重试。</p>"

        await db.execute(
            update(WeeklyDigest)
            .where(WeeklyDigest.digest_type == "paper", WeeklyDigest.is_latest == True)
            .values(is_latest=False)
        )

        title = f"论文学术周报 ({week_start.isoformat()} ~ {week_end.isoformat()})"
        digest = WeeklyDigest(
            digest_type="paper",
            title=title,
            content=content,
            week_start=week_start,
            week_end=week_end,
            is_latest=True,
        )
        db.add(digest)
        await db.commit()
        await db.refresh(digest)

        logger.info(f"Paper digest created: id={digest.id}, papers={len(papers)}")
        return {"id": digest.id, "title": title, "paper_count": len(papers)}


async def generate_news_digest() -> dict | None:
    week_end = date.today()
    week_start = week_end - timedelta(days=7)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(NewsItem)
            .where(NewsItem.published_date >= week_start, NewsItem.published_date <= week_end)
            .order_by(NewsItem.published_date.desc())
            .limit(50)
        )
        items = result.scalars().all()

        if not items:
            logger.info("No news items found for weekly digest")
            return None

        news_texts = []
        for n in items:
            date_str = n.published_date.strftime("%m-%d") if n.published_date else ""
            news_texts.append(f"- [{date_str}] [{n.source_name}] {n.title}")
        prompt = NEWS_SUMMARY_PROMPT + "\n".join(news_texts)

        try:
            content = await call_llm(prompt, NEWS_SYSTEM_PROMPT)
        except Exception as e:
            logger.error(f"LLM call failed for news digest: {e}")
            content = f"<p>本周共收录 {len(items)} 条行业动态。LLM 摘要生成失败：{e}</p><p>请检查 LLM 配置或稍后重试。</p>"

        await db.execute(
            update(WeeklyDigest)
            .where(WeeklyDigest.digest_type == "news", WeeklyDigest.is_latest == True)
            .values(is_latest=False)
        )

        title = f"行业动态周报 ({week_start.isoformat()} ~ {week_end.isoformat()})"
        digest = WeeklyDigest(
            digest_type="news",
            title=title,
            content=content,
            week_start=week_start,
            week_end=week_end,
            is_latest=True,
        )
        db.add(digest)
        await db.commit()
        await db.refresh(digest)

        logger.info(f"News digest created: id={digest.id}, news={len(items)}")
        return {"id": digest.id, "title": title, "news_count": len(items)}
