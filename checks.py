import re
import subprocess
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


def main() -> int:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "rendercv_output" / "Afshin_Hasani_CV.pdf"
    cv = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))["cv"]
    errors = []
    if "phone" in cv:
        errors.append("cv.yaml contains a phone number; pass it with --cv.phone locally instead")
    errors += check_pdf(pdf, cv)
    for error in errors:
        print(f"FAIL {error}")
    if not errors:
        print(f"OK {pdf.name}: {EXPECTED_PAGES} pages, extraction keeps dates, skills and degrees together")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
