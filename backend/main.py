from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import init_db, get_db
from models.report import ReportSection
from models.paper import Paper
from routers import report, paper

env = Environment(loader=FileSystemLoader("templates"))


def render(name: str, **kwargs) -> HTMLResponse:
    template = env.get_template(name)
    return HTMLResponse(template.render(**kwargs))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    import scheduler
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="AI Agent Platform", version="2.1.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(report.router)
app.include_router(paper.router)


async def get_all_sections(db: AsyncSession):
    result = await db.execute(
        select(ReportSection).order_by(ReportSection.sort_order)
    )
    return result.scalars().all()


# -- HTML page routes --

@app.get("/", response_class=HTMLResponse)
async def page_index(db: AsyncSession = Depends(get_db)):
    sections = await get_all_sections(db)
    return render("index.html", sections=sections, current_page="home")


@app.get("/report", response_class=HTMLResponse)
async def page_report(db: AsyncSession = Depends(get_db)):
    sections = await get_all_sections(db)
    return render("index.html", sections=sections, current_page="report")


@app.get("/report/{section_key}", response_class=HTMLResponse)
async def page_report_section(section_key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReportSection).where(ReportSection.section_key == section_key)
    )
    section = result.scalar_one_or_none()
    return render("report.html", section=section, current_page="report")


@app.get("/papers", response_class=HTMLResponse)
async def page_papers(
    source: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
):
    q = select(Paper)
    if source:
        q = q.where(Paper.source == source)
    if keyword:
        pattern = f"%{keyword}%"
        q = q.where((Paper.title.ilike(pattern)) | (Paper.abstract.ilike(pattern)))
    q = q.order_by(Paper.published_date.desc(), Paper.id.desc())
    q = q.offset((page - 1) * 20).limit(20)
    result = await db.execute(q)
    papers = result.scalars().all()

    # Count total
    from sqlalchemy import func
    count_q = select(func.count()).select_from(Paper)
    if source:
        count_q = count_q.where(Paper.source == source)
    if keyword:
        pattern = f"%{keyword}%"
        count_q = count_q.where((Paper.title.ilike(pattern)) | (Paper.abstract.ilike(pattern)))
    total = (await db.execute(count_q)).scalar() or 0

    return render("papers.html", papers=papers, source=source, keyword=keyword,
                  page=page, total=total, current_page="papers")


@app.get("/papers/{paper_id}", response_class=HTMLResponse)
async def page_paper_detail(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    return render("paper_detail.html", paper=paper, current_page="papers")


@app.get("/news", response_class=HTMLResponse)
async def page_news():
    return render("base.html", current_page="news")


# -- health --

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.1.0"}
