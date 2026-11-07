import argparse
import re
import subprocess
from html.parser import HTMLParser
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader

ROOT = Path(__file__).parent
EXPECTED_PAGES = 2
DATE_RANGE = r"(?:[A-Z][a-z]+ )?(?P<start>\d{4}) – (?:present|(?:[A-Z][a-z]+ )?\d{4})"
PHONE = re.compile(r"\+\d{1,3}[\s\d]{8,}")


def pdftotext(pdf: Path, mode: str) -> str:
    result = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", mode, str(pdf), "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout


def pypdf_text(pdf: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)


def normalize(text: str) -> list[str]:
    return [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]


def check_experience(lines: list[str], cv: dict) -> list[str]:
    errors = []
    for entry in cv["sections"]["experience"]:
        company = entry["company"]
        start = str(entry.get("start_date") or entry.get("date", ""))[:4]
        pattern = re.compile(DATE_RANGE + r" " + re.escape(company) + r" —")
        match = next((m for line in lines if (m := pattern.search(line))), None)
        if match is None:
            errors.append(f"date is not on the same line as '{company}'")
        elif match["start"] != start:
            errors.append(f"'{company}' shows start year {match['start']}, expected {start}")
    return errors


def check_skills(lines: list[str], cv: dict) -> list[str]:
    errors = []
    for skill in cv["sections"]["skills"]:
        head = f"{skill['label']}: {skill['details'].split(',')[0].strip()}"
        if not any(line.startswith(head) for line in lines):
            errors.append(f"skill label '{skill['label']}' is separated from its values")
    return errors


def check_education(lines: list[str], cv: dict) -> list[str]:
    errors = []
    for item in cv["sections"]["education"]:
        head = f"{item['degree']}, {item['area']}"
        years = str(item["years"])
        if not any(head in line and years in line for line in lines):
            errors.append(f"'{head}' is separated from '{years}'")
    return errors


def check_pdf(pdf: Path, cv: dict) -> list[str]:
    errors = []
    pages = len(PdfReader(pdf).pages)
    if pages != EXPECTED_PAGES:
        errors.append(f"PDF has {pages} pages, expected {EXPECTED_PAGES}")
    extractions = {
        "pdftotext -raw": pdftotext(pdf, "-raw"),
        "pdftotext -layout": pdftotext(pdf, "-layout"),
        "pypdf": pypdf_text(pdf),
    }
    for name, text in extractions.items():
        lines = normalize(text)
        for error in check_experience(lines, cv) + check_skills(lines, cv) + check_education(lines, cv):
            errors.append(f"[{name}] {error}")
        if PHONE.search(text):
            errors.append(f"[{name}] PDF contains a phone number")
    return errors


SECTION_HEADINGS = ["context", "problem", "constraints", "approach", "outcome", "stack"]
MOTION = re.compile(r"\b(animation|transition)\s*:|@keyframes")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.text: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.text.append(data)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.plain = re.sub(r"\s+", " ", " ".join(parser.text))
    return parser


def resolve(site: Path, page: Path, ref: str) -> tuple[Path, str]:
    path, _, anchor = ref.partition("#")
    if not path:
        return page, anchor
    target = site / path.lstrip("/") if path.startswith("/") else page.parent / path
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target, anchor


def check_site(site: Path, cv: dict, portfolio: dict) -> list[str]:
    errors = []
    pages = {p: parse(p) for p in site.rglob("*.html")}
    for page, parsed in pages.items():
        name = page.relative_to(site).as_posix()
        for ref in parsed.refs:
            if re.match(r"^(https?:|mailto:|tel:|data:)", ref):
                continue
            target, anchor = resolve(site, page, ref.split("?")[0])
            if not target.exists():
                errors.append(f"[{name}] broken link or asset: {ref}")
            elif anchor and target.suffix == ".html" and anchor not in pages.get(target, parse(target)).ids:
                errors.append(f"[{name}] missing anchor: {ref}")

    home = pages.get(site / "index.html")
    if home is None:
        return errors + ["index.html was not built"]
    for point in portfolio["proof_points"]:
        for field in ("title", "fact", "role"):
            if point[field] not in home.plain:
                errors.append(f"[index.html] Proof Point {field} missing from static HTML: {point[field]}")
    for entry in cv["sections"]["experience"]:
        if "start_date" in entry and f"{entry['company']} — {entry['position']}" not in home.plain:
            errors.append(f"[index.html] role line missing from static HTML: {entry['company']}")

    companies = {e["company"] for e in cv["sections"]["experience"]}
    for path in sorted((ROOT / "case-studies").glob("*.md")):
        front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        for company in front["company"].split(" · "):
            if company not in companies:
                errors.append(f"[case-studies/{path.name}] company '{company}' is not a role in cv.yaml")
        page = pages.get(site / "case-studies" / path.stem / "index.html")
        if page is None:
            errors.append(f"[case-studies/{path.stem}] page was not built")
            continue
        for heading in SECTION_HEADINGS:
            if heading not in page.plain:
                errors.append(f"[case-studies/{path.stem}] section '{heading}' missing from static HTML")
        if front["role"] not in page.plain:
            errors.append(f"[case-studies/{path.stem}] Role line missing from static HTML")
    if not any(p.relative_to(site).as_posix() in portfolio["site"]["resume_path"] for p in site.glob("*.pdf")):
        errors.append(f"Resume PDF missing at {portfolio['site']['resume_path']}")

    for css in site.rglob("*.css"):
        text = css.read_text(encoding="utf-8")
        start = text.find("@media (prefers-reduced-motion:no-preference){")
        end = text.find("\n}\n", start) if start >= 0 else -1
        outside = text[:start] + text[end:] if start >= 0 else text
        if MOTION.search(outside):
            errors.append(f"[{css.name}] animation or transition outside prefers-reduced-motion: no-preference")
    return errors


def main() -> int:
    args = argparse.ArgumentParser()
    args.add_argument("pdf", nargs="?", type=Path, default=ROOT / "rendercv_output" / "Afshin_Hasani_CV.pdf")
    args.add_argument("--site", type=Path)
    opts = args.parse_args()
    cv = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))["cv"]
    errors = []
    if "phone" in cv:
        errors.append("cv.yaml contains a phone number; pass it with --cv.phone locally instead")
    errors += check_pdf(opts.pdf, cv)
    if opts.site:
        portfolio = yaml.safe_load((ROOT / "portfolio.yaml").read_text(encoding="utf-8"))
        errors += check_site(opts.site, cv, portfolio)
    for error in errors:
        print(f"FAIL {error}")
    if not errors:
        scope = f" and site {opts.site}" if opts.site else ""
        print(f"OK {opts.pdf.name}{scope}: all checks passed")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
