import shutil
import sys
from datetime import date
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
PDF = ROOT / "rendercv_output" / "Afshin_Hasani_CV.pdf"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))


def split_sections(html: str) -> list[dict]:
    sections = []
    for chunk in html.split("<h2>")[1:]:
        heading, body = chunk.split("</h2>", 1)
        heading = heading.strip()
        sections.append({"heading": heading, "id": heading.lower().replace(" ", "-"), "body": body.strip()})
    return sections


LANGS = {"en": "", "fa": "fa"}
# A project card shows these fields from its Case Study, so they are written once, in the Case Study frontmatter.
SHARED_FIELDS = ("title", "companies", "period", "role", "mockup", "image", "image_w", "image_h", "image_alt", "image_caption")
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def content_dir(lang: str) -> Path:
    return ROOT / LANGS[lang]


def load_case_studies(lang: str) -> list[dict]:
    studies = []
    for path in sorted((content_dir(lang) / "case-studies").glob("*.md")):
        _, front, body = path.read_text(encoding="utf-8").split("---", 2)
        meta = yaml.safe_load(front)
        html = markdown.markdown(body, extensions=["fenced_code"])
        studies.append({**meta, "slug": path.stem, "sections": split_sections(html)})
    studies.sort(key=lambda s: s["order"])
    for i, study in enumerate(studies):
        study["prev"] = studies[i - 1]
        study["next"] = studies[(i + 1) % len(studies)]
    return studies


def load_portfolio(lang: str) -> dict:
    base = load_yaml("portfolio.yaml")
    if lang == "en":
        return base
    site = yaml.safe_load((content_dir(lang) / "portfolio.yaml").read_text(encoding="utf-8"))
    site["site"] = {**base["site"], **site.get("site", {})}
    return site


def career(cv: dict, site: dict) -> list[dict]:
    rows = []
    for entry in cv["sections"]["experience"]:
        if "start_date" not in entry:
            continue
        info = site["companies"].get(entry["company"], {})
        start = str(entry["start_date"])[:4]
        current = entry["end_date"] == "present"
        end = site["ui"]["now"] if current else str(entry["end_date"])[:4]
        rows.append(
            {
                "key": entry["company"],
                "company": info.get("name", entry["company"]),
                "position": info.get("position", entry["position"]),
                "years": f"{start} – {end}",
                "note": info.get("note", ""),
                "current": current,
            }
        )
    return rows


def make_env(lang: str) -> Environment:
    env = Environment(
        loader=FileSystemLoader(ROOT / "site" / "templates"),
        undefined=StrictUndefined,
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["num"] = (lambda v: str(v).translate(FA_DIGITS)) if lang == "fa" else str
    return env


def proof_points(site: dict, studies: list[dict], lang: str) -> list[dict]:
    by_slug = {s["slug"]: s for s in studies}
    points = []
    for point in site["proof_points"]:
        study = by_slug.get(point["slug"])
        if study is None:
            sys.exit(f"[{lang}] Proof Point without a Case Study: {point['slug']}")
        duplicated = [f for f in SHARED_FIELDS if f in point]
        if duplicated:
            sys.exit(f"[{lang}] Proof Point {point['slug']} repeats {', '.join(duplicated)}; set it in the Case Study only")
        points.append({**{f: study[f] for f in SHARED_FIELDS if f in study}, **point})
    return points


def build_lang(cv: dict, lang: str) -> int:
    env = make_env(lang)
    site = load_portfolio(lang)
    studies = load_case_studies(lang)
    site["proof_points"] = proof_points(site, studies, lang)

    root = f"/{LANGS[lang]}/" if LANGS[lang] else "/"
    other_root = f"/{LANGS[site['ui']['other_lang']]}/".replace("//", "/")
    out = OUT / LANGS[lang]
    out.mkdir(parents=True, exist_ok=True)
    ctx = {"cv": cv, "site": site, "ui": site["ui"], "studies": studies, "year": date.today().year, "root": root}

    home = env.get_template("home.html.j2").render(**ctx, page="home", path=root, alt=other_root, career=career(cv, site))
    (out / "index.html").write_text(home, encoding="utf-8")

    for study in studies:
        target = out / "case-studies" / study["slug"]
        target.mkdir(parents=True)
        path = f"{root}case-studies/{study['slug']}/"
        alt = f"{other_root}case-studies/{study['slug']}/"
        html = env.get_template("case-study.html.j2").render(**ctx, page="case", path=path, alt=alt, study=study)
        (target / "index.html").write_text(html, encoding="utf-8")
    return len(studies)


def build() -> None:
    cv = load_yaml("cv.yaml")["cv"]

    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    shutil.copytree(ROOT / "site" / "static", OUT, dirs_exist_ok=True)

    counts = {lang: build_lang(cv, lang) for lang in LANGS}

    site = load_portfolio("en")
    env = make_env("en")
    ctx = {"cv": cv, "site": site, "ui": site["ui"], "studies": load_case_studies("en"), "year": date.today().year, "root": "/"}
    (OUT / "404.html").write_text(env.get_template("404.html.j2").render(**ctx, page="404", path="/", alt="/fa/"), encoding="utf-8")
    sitemap = env.get_template("sitemap.xml.j2").render(**ctx, langs=LANGS, today=date.today().isoformat())
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    if PDF.exists():
        shutil.copy(PDF, OUT / site["site"]["resume_path"].lstrip("/"))
    print(f"Built {OUT}: " + ", ".join(f"{lang} with {n} Case Studies" for lang, n in counts.items()))


if __name__ == "__main__":
    build()
