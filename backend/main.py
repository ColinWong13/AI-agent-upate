from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import init_db, get_db
from models.report import ReportSection
from models.paper import Paper
from models.user import User, UserFavorite, UserNote
from auth import current_user
from routers import report, paper, news, user

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


app = FastAPI(title="AI Agent Platform", version="2.3.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(report.router)
app.include_router(paper.router)
app.include_router(news.router)
app.include_router(user.router)


async def get_all_sections(db: AsyncSession):
    result = await db.execute(select(ReportSection).order_by(ReportSection.sort_order))
    return result.scalars().all()


async def get_favorites_map(db: AsyncSession, user: User, item_type: str) -> set[int]:
    """Return set of item_ids this user has favorited for a given type."""
    if user is None:
        return set()
    result = await db.execute(
        select(UserFavorite.item_id).where(
            UserFavorite.user_id == user.id,
            UserFavorite.item_type == item_type,
        )
    )
    return {r[0] for r in result}


# -- HTML page routes (user is optional, injected for nav state) --

@app.get("/", response_class=HTMLResponse)
async def page_index(user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    sections = await get_all_sections(db)
    return render("index.html", sections=sections, current_page="home", user=user)


@app.get("/report", response_class=HTMLResponse)
async def page_report(user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    sections = await get_all_sections(db)
    return render("index.html", sections=sections, current_page="report", user=user)


@app.get("/report/{section_key}", response_class=HTMLResponse)
async def page_report_section(section_key: str, user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportSection).where(ReportSection.section_key == section_key))
    section = result.scalar_one_or_none()
    return render("report.html", section=section, current_page="report", user=user)


@app.get("/papers", response_class=HTMLResponse)
async def page_papers(
    source: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    user: User | None = Depends(current_user),
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

    count_q = select(func.count()).select_from(Paper)
    if source:
        count_q = count_q.where(Paper.source == source)
    if keyword:
        count_q = count_q.where((Paper.title.ilike(pattern)) | (Paper.abstract.ilike(pattern)))
    total = (await db.execute(count_q)).scalar() or 0

    favorites = await get_favorites_map(db, user, "paper")

    return render("papers.html", papers=papers, source=source, keyword=keyword,
                  page=page, total=total, current_page="papers", user=user,
                  favorites=favorites)


@app.get("/papers/{paper_id}", response_class=HTMLResponse)
async def page_paper_detail(paper_id: int, user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    # Get user's note for this paper
    note_content = ""
    note_id = None
    is_favorited = False
    if user:
        nr = await db.execute(
            select(UserNote).where(UserNote.user_id == user.id, UserNote.item_type == "paper", UserNote.item_id == paper_id)
        )
        note = nr.scalar_one_or_none()
        if note:
            note_content = note.content
            note_id = note.id
        fr = await db.execute(
            select(UserFavorite.id).where(UserFavorite.user_id == user.id, UserFavorite.item_type == "paper", UserFavorite.item_id == paper_id)
        )
        is_favorited = fr.scalar_one_or_none() is not None

    return render("paper_detail.html", paper=paper, current_page="papers", user=user,
                  note_content=note_content, note_id=note_id, is_favorited=is_favorited)


@app.get("/news", response_class=HTMLResponse)
async def page_news(
    category: str | None = None,
    page: int = 1,
    user: User | None = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    from models.news import NewsItem
    q = select(NewsItem)
    if category:
        q = q.where(NewsItem.category == category)
    q = q.order_by(NewsItem.published_date.desc(), NewsItem.id.desc())
    q = q.offset((page - 1) * 20).limit(20)
    result = await db.execute(q)
    items = result.scalars().all()

    count_q = select(func.count()).select_from(NewsItem)
    if category:
        count_q = count_q.where(NewsItem.category == category)
    total = (await db.execute(count_q)).scalar() or 0

    cat_result = await db.execute(select(NewsItem.category).distinct())
    categories = sorted([r[0] for r in cat_result if r[0]])

    favorites = await get_favorites_map(db, user, "news")

    return render("news.html", news_items=items, categories=categories,
                  active_category=category, page=page, total=total, current_page="news",
                  user=user, favorites=favorites)


@app.get("/admin", response_class=HTMLResponse)
async def page_admin(user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    from models.news import NewsItem
    result = await db.execute(select(NewsItem).order_by(NewsItem.published_date.desc()).limit(50))
    items = result.scalars().all()
    return render("admin.html", items=items, current_page="", user=user)


# -- auth pages --

@app.get("/login", response_class=HTMLResponse)
async def page_login(user: User | None = Depends(current_user)):
    return render("login.html", current_page="", user=user)


@app.get("/register", response_class=HTMLResponse)
async def page_register(user: User | None = Depends(current_user)):
    return render("register.html", current_page="", user=user)


# -- user pages --

@app.get("/favorites", response_class=HTMLResponse)
async def page_favorites(user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user is None:
        return RedirectResponse("/login", status_code=302)
    result = await db.execute(
        select(UserFavorite).where(UserFavorite.user_id == user.id).order_by(UserFavorite.created_at.desc())
    )
    favs = result.scalars().all()
    # Resolve titles
    fav_data = []
    for f in favs:
        title = ""
        if f.item_type == "paper":
            pr = await db.execute(select(Paper.title).where(Paper.id == f.item_id))
            row = pr.scalar_one_or_none()
            title = row if row else "(已删除)"
        elif f.item_type == "news":
            from models.news import NewsItem
            nr = await db.execute(select(NewsItem.title).where(NewsItem.id == f.item_id))
            row = nr.scalar_one_or_none()
            title = row if row else "(已删除)"
        fav_data.append({"id": f.id, "item_type": f.item_type, "item_id": f.item_id, "title": title, "created_at": f.created_at})
    return render("favorites.html", favorites=fav_data, current_page="", user=user)


@app.get("/notes", response_class=HTMLResponse)
async def page_notes(user: User | None = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user is None:
        return RedirectResponse("/login", status_code=302)
    result = await db.execute(
        select(UserNote).where(UserNote.user_id == user.id).order_by(UserNote.updated_at.desc())
    )
    notes = result.scalars().all()
    note_data = []
    for n in notes:
        title = ""
        if n.item_type == "paper":
            pr = await db.execute(select(Paper.title).where(Paper.id == n.item_id))
            row = pr.scalar_one_or_none()
            title = row if row else "(已删除)"
        note_data.append({"id": n.id, "item_type": n.item_type, "item_id": n.item_id, "title": title, "content": n.content, "updated_at": n.updated_at})
    return render("notes.html", notes=note_data, current_page="", user=user)


# -- health --

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.3.0"}
