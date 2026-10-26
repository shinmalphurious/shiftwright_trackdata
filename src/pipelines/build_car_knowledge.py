"""Build per-car knowledge from the official iRacing car manuals.

Input:  $SHIFTWRIGHT_DATA_ROOT/iracing-manuals/*.pdf (iRacing's user manuals, kept outside git).
Output: generated/car_knowledge/<slug>.json, one per manual, plus generated/car_knowledge/index.json.

Each file holds the manual's own title (e.g. "MCLAREN 720S GT3"), its tech specs, and its sections
as written (introduction, in-car adjustments, setup chapters), so the platform can give the coach
car-specific context without inventing anything. Dash-display pages are left out (they describe
the screen, not the car).

The extracted text is iRacing's: generated/car_knowledge/ is git-ignored. Regenerate with
    python -m src.pipelines.build_car_knowledge

Matching a session's car name to a manual is done by the platform (CarKnowledgeStore) from the
manual title and `config/car_knowledge_aliases.json` (exact iRacing car name -> manual slug).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.shared.paths import DATA_ROOT, GENERATED  # noqa: E402

MANUALS = DATA_ROOT / "iracing-manuals"
OUT = GENERATED / "car_knowledge"

HEADER = re.compile(r"^\s*(?P<car>[A-Z0-9][A-Z0-9 .\-/&']+?)\s*\|\s*(?P<section>[A-Z0-9][A-Z0-9 .,\-/&'()]+?)\s*$", re.M)
SKIP_SECTIONS = ("DASH", "TABLE OF CONTENTS", "CONTENTS")
SKIP_FILES = ("user-guide",)            # general guides, not a car


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_header(text: str) -> tuple[str | None, str | None]:
    """("MCLAREN 720S GT3", "INTRODUCTION") from the page's "CAR | SECTION" line, skipping the
    "CAR | USER MANUAL" running header."""
    car = None
    for m in HEADER.finditer(text):
        section = m["section"].strip()
        if section == "USER MANUAL":
            car = car or m["car"].strip()
            continue
        return m["car"].strip(), section
    return car, None


def extract(path: Path) -> dict:
    reader = PdfReader(str(path))
    title = None
    sections: dict[str, list[str]] = {}
    order: list[str] = []
    current = "INTRODUCTION"
    for page in reader.pages:
        text = page.extract_text() or ""
        car, section = page_header(text)
        title = title or car
        if section:
            current = section
        if any(s in current for s in SKIP_SECTIONS):
            continue
        body = HEADER.sub("", text)
        body = re.sub(r"^\s*\d+\s*$", "", body, flags=re.M)          # page numbers
        if current not in sections:
            sections[current] = []
            order.append(current)
        sections[current].append(clean(body))
    return {
        "slug": slug(path.stem),
        "manual_file": path.name,
        "title": title or path.stem,
        "pages": len(reader.pages),
        "sections": [{"title": name, "text": clean("\n\n".join(sections[name]))}
                     for name in order if "".join(sections[name]).strip()],
    }


def main() -> None:
    if not MANUALS.is_dir():
        sys.exit(f"No manuals folder: {MANUALS}")
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for path in sorted(MANUALS.glob("*.pdf")):
        if any(k in slug(path.stem) for k in SKIP_FILES):
            continue
        try:
            car = extract(path)
        except Exception as exc:                      # a damaged PDF must not stop the rest
            print(f"skip {path.name}: {exc}")
            continue
        car["extracted_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        (OUT / f"{car['slug']}.json").write_text(json.dumps(car, indent=1, ensure_ascii=False), encoding="utf-8")
        index.append({"slug": car["slug"], "title": car["title"], "manual_file": car["manual_file"],
                      "sections": [s["title"] for s in car["sections"]]})
        print(f"{car['slug']}: {car['title']} ({len(car['sections'])} sections)")
    (OUT / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(index)} cars -> {OUT}")


if __name__ == "__main__":
    main()
