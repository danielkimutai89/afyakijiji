from flask import Blueprint, render_template, request, abort

from .models import ContentPage, CareProgram
from .content_meta import NEIGHBOURHOODS, NATIONAL_NUMBERS, ABOUT_STORY, ABOUT_DISCLAIMER

main_bp = Blueprint("main", __name__)

# Maps a house's slug to the triage flow node (in routes_symptoms.FLOW) that
# best matches it, so a house detail page can offer a direct "Check your
# symptoms" link into the right branch instead of the generic start screen.
HOUSE_TRIAGE_LINKS = {
    "maternal-child-health": "pregnancy",
    "child-nutrition": "child_fever",
    "pneumonia": "breathing",
    "malaria": "malaria_symptoms",
    "diarrhea-dehydration": "diarrhea_symptoms",
    "mental-health": "mental_health_check",
}


@main_bp.route("/")
def index():
    lang = request.args.get("lang", "en")
    pages = ContentPage.query.filter_by(language=lang, audience="public").all()

    neighbourhood_keys = {n["key"] for n in NEIGHBOURHOODS}
    by_category = {}
    for content_page in pages:
        by_category.setdefault(content_page.category, []).append(content_page)

    # Group the 16 "houses" under their neighbourhood, in the order defined
    # in content_meta.NEIGHBOURHOODS; anything else public (the practical
    # guides) is shown separately below.
    neighbourhoods = [
        {**n, "pages": sorted(by_category.get(n["key"], []), key=lambda p: p.title)}
        for n in NEIGHBOURHOODS
    ]
    practical_pages = sorted(
        [p for p in pages if p.category not in neighbourhood_keys],
        key=lambda p: p.title,
    )

    return render_template(
        "page.html",
        page="index",
        pages=pages,
        neighbourhoods=neighbourhoods,
        practical_pages=practical_pages,
        lang=lang,
    )


@main_bp.route("/topic/<slug>")
def topic_detail(slug):
    content_page = ContentPage.query.filter_by(slug=slug, audience="public").first()
    if content_page is None:
        abort(404)
    matching_program = CareProgram.query.filter_by(house_slug=slug).first()
    triage_node = HOUSE_TRIAGE_LINKS.get(slug)
    return render_template(
        "page.html",
        page="topic_detail",
        content_page=content_page,
        matching_program=matching_program,
        triage_node=triage_node,
    )


@main_bp.route("/emergency")
def emergency():
    """Pull every 'SEEK HELP:' block out of the public houses into one page,
    alongside the verified national emergency/helpline numbers.

    Relies on the ContentPage.body convention (see seed.py's module
    docstring): a "SEEK HELP:" line followed by "- " bullet lines.
    """
    pages = ContentPage.query.filter_by(language="en", audience="public").all()
    groups = []
    for content_page in pages:
        parts = content_page.body.split("\n\n")
        seek_help_lines = []
        for part in parts:
            if part.startswith("SEEK HELP:"):
                seek_help_lines = [
                    line.lstrip("- ").strip()
                    for line in part.split("\n")[1:]
                    if line.strip()
                ]
        if seek_help_lines:
            groups.append({"content_page": content_page, "signs": seek_help_lines})
    return render_template(
        "page.html", page="emergency", groups=groups, national_numbers=NATIONAL_NUMBERS
    )


@main_bp.route("/about")
def about():
    return render_template(
        "page.html", page="about", story=ABOUT_STORY, disclaimer=ABOUT_DISCLAIMER
    )
