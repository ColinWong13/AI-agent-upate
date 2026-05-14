"""
Parse the existing static index.html and migrate its content into report_sections table.
Run this script once to seed the database.
"""
import re
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

# Add parent to sys.path so we can import from backend
sys.path.insert(0, str(Path(__file__).resolve().parent))
from database import SyncSessionLocal
from models.report import ReportSection


HTML_PATH = Path(__file__).resolve().parent.parent.parent / "index.html"

def transform_colors(html: str) -> str:
    """Convert old corporate blue colors to Newsprint palette."""
    replacements = [
        # Blue gradients → solid black
        ("linear-gradient(135deg, #1F497D 0%, #3660A0 60%, #4F81BD 100%)", "#111111"),
        ("linear-gradient(135deg, #1F497D, #3660A0)", "#111111"),
        ("linear-gradient(135deg, #3660A0, #4F81BD)", "#222222"),
        ("linear-gradient(135deg, #4F81BD, #6FA1D8)", "#333333"),
        ("linear-gradient(135deg, #c0392b, #e74c3c)", "#CC0000"),
        ("linear-gradient(135deg, #1F497D, #E8A020)", "#111111"),
        ("linear-gradient(135deg, #E8A020, #F5B84D)", "#CC0000"),
        ("linear-gradient(135deg, #24292e, #3a4a5c)", "#111111"),
        ("linear-gradient(135deg, #5a7a9a, #7a9aba)", "#444444"),
        ("linear-gradient(135deg, #e8f0fb, #fff)", "transparent"),
        ("linear-gradient(180deg, var(--bg) 0%, #e8eef8 100%)", "transparent"),
        # Single hex colors
        ("#1F497D", "#111111"),
        ("#3660A0", "#222222"),
        ("#4F81BD", "#333333"),
        ("#DCE6F1", "#E5E5E0"),
        ("#E8A020", "#CC0000"),
        ("#e8f0fb", "#F5F5F5"),
        ("#f0f4fa", "#F5F5F5"),
        ("#dce8f8", "#E5E5E0"),
        # Old CSS variables → new ones or hardcoded
        ("var(--blue-dark)", "var(--fg)"),
        ("var(--blue-mid)", "var(--neutral-700)"),
        ("var(--blue-light)", "var(--neutral-500)"),
        ("var(--blue-pale)", "var(--neutral-100)"),
        ("var(--bg)", "var(--bg)"),
        ("var(--white)", "var(--bg)"),
        ("var(--border)", "var(--border)"),
        ("var(--text)", "var(--fg)"),
        ("var(--text-light)", "var(--neutral-600)"),
        ("var(--shadow)", "none"),
        ("var(--accent)", "var(--accent)"),
        # Class-based fixes
        ('"background:#1F497D"', '"background:#111111"'),
        ('"background:#3660A0"', '"background:#222222"'),
        ('"background:#4F81BD"', '"background:#333333"'),
        ('"background:#5a7a9a"', '"background:#444444"'),
        ('"background:#c0392b"', '"background:#CC0000"'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)
    return html


SECTION_META = {
    "concepts": {"title": "一、核心概念与 Agent 原理", "sort_order": 1},
    "platforms": {"title": "二、主流 Agent 平台深度对比", "sort_order": 2},
    "data": {"title": "三、垂直领域 Agent 竞品分析", "sort_order": 3},
    "skills": {"title": "四、面向产品研发的 Agent Skills", "sort_order": 4},
    "cc": {"title": "五、Claude Code 配置指南", "sort_order": 5},
    "summary": {"title": "六、总结与建议", "sort_order": 6},
    "news": {"title": "七、行业动态", "sort_order": 7},
}


def extract_sections() -> list[dict]:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    sections = []

    for section_id, meta in SECTION_META.items():
        el = soup.find(id=section_id)
        if el is None:
            print(f"  WARN: section id='{section_id}' not found, skipping")
            continue

        # Extract inner HTML and strip the section-title div (template adds it)
        inner_soup = BeautifulSoup("".join(str(c) for c in el.contents), "lxml")
        title_div = inner_soup.find("div", class_="section-title")
        if title_div:
            title_div.decompose()
        inner = "".join(str(c) for c in inner_soup.contents)
        # For sections that are wrappers (like data), include the video section wrapper etc.
        # The news section has an outer wrapping div, grab more context
        if section_id == "news":
            parent = el.parent
            if parent and parent.name == "div" and "container" in parent.get("class", []):
                parent = parent.parent
            inner = "".join(str(c) for c in parent.contents) if parent else inner

        inner = transform_colors(inner)
        sections.append({
            "section_key": section_id,
            "title": meta["title"],
            "content_json": {"html": inner, "type": "raw_html"},
            "sort_order": meta["sort_order"],
        })
        print(f"  OK: extracted section '{section_id}' ({meta['title']})")

    return sections


def extract_hero_section() -> dict:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    hero = soup.find("div", class_="hero")
    if hero:
        return {"html": "".join(str(c) for c in hero.contents)}
    return {"html": ""}


def extract_nav_and_footer() -> tuple[str, str]:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    nav = soup.find("nav")
    nav_html = "".join(str(c) for c in nav.contents) if nav else ""

    footer = soup.find("footer")
    footer_html = "".join(str(c) for c in footer.contents) if footer else ""

    return nav_html, footer_html


def migrate():
    print("Parsing index.html...")
    sections = extract_sections()
    print(f"Extracted {len(sections)} sections.")
    print("Seeding database...")

    with SyncSessionLocal() as db:
        for sec in sections:
            existing = db.query(ReportSection).filter_by(section_key=sec["section_key"]).first()
            if existing:
                existing.title = sec["title"]
                existing.content_json = sec["content_json"]
                existing.sort_order = sec["sort_order"]
            else:
                db.add(ReportSection(**sec))
        db.commit()

    print("Migration complete.")


if __name__ == "__main__":
    migrate()
