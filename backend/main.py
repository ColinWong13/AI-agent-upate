from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import init_db, get_db
from models.report import ReportSection
from routers import report

env = Environment(loader=FileSystemLoader("templates"))


def render(name: str, **kwargs) -> HTMLResponse:
    template = env.get_template(name)
    return HTMLResponse(template.render(**kwargs))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AI Agent Platform", version="2.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(report.router)


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
async def page_papers():
    return render("base.html", current_page="papers")


@app.get("/news", response_class=HTMLResponse)
async def page_news():
    return render("base.html", current_page="news")


# -- health --

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
