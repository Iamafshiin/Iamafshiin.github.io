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


def load_case_studies() -> list[dict]:
    studies = []
    for path in sorted((ROOT / "case-studies").glob("*.md")):
        _, front, body = path.read_text(encoding="utf-8").split("---", 2)
        meta = yaml.safe_load(front)
        html = markdown.markdown(body, extensions=["fenced_code"])
        studies.append({**meta, "slug": path.stem, "sections": split_sections(html)})
    studies.sort(key=lambda s: s["order"])
    for i, study in enumerate(studies):
        study["prev"] = studies[i - 1]
        study["next"] = studies[(i + 1) % len(studies)]
    return studies


def career(cv: dict, notes: dict) -> list[dict]:
    rows = []
    for entry in cv["sections"]["experience"]:
        if "start_date" not in entry:
            continue
        start = str(entry["start_date"])[:4]
        end = "now" if entry["end_date"] == "present" else str(entry["end_date"])[:4]
        rows.append(
            {
                "company": entry["company"],
                "position": entry["position"],
                "years": f"{start} – {end}",
                "note": notes.get(entry["company"], ""),
                "current": end == "now",
            }
        )
    return rows


def build() -> None:
    cv = load_yaml("cv.yaml")["cv"]
    site = load_yaml("portfolio.yaml")
    studies = load_case_studies()
    slugs = {s["slug"] for s in studies}
    missing = [p["slug"] for p in site["proof_points"] if p["slug"] not in slugs]
    if missing:
        sys.exit(f"Proof Point without a Case Study: {', '.join(missing)}")

    env = Environment(
        loader=FileSystemLoader(ROOT / "site" / "templates"),
        undefined=StrictUndefined,
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    ctx = {"cv": cv, "site": site, "studies": studies, "year": date.today().year}

    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    shutil.copytree(ROOT / "site" / "static", OUT, dirs_exist_ok=True)

    home = env.get_template("home.html.j2").render(**ctx, page="home", career=career(cv, site["career_notes"]))
    (OUT / "index.html").write_text(home, encoding="utf-8")

    for study in studies:
        target = OUT / "case-studies" / study["slug"]
        target.mkdir(parents=True)
        html = env.get_template("case-study.html.j2").render(**ctx, page="case", study=study)
        (target / "index.html").write_text(html, encoding="utf-8")

    (OUT / "404.html").write_text(env.get_template("404.html.j2").render(**ctx, page="404"), encoding="utf-8")
    sitemap = env.get_template("sitemap.xml.j2").render(**ctx, today=date.today().isoformat())
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    if PDF.exists():
        shutil.copy(PDF, OUT / site["site"]["resume_path"].lstrip("/"))
    print(f"Built {OUT} with {len(studies)} Case Studies")


if __name__ == "__main__":
    build()
