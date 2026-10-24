from pathlib import Path
import re
import json

VECTOR_ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

results = []

for svg in VECTOR_ROOT.rglob("active.svg"):

    text = svg.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    paths = len(
        re.findall(
            r"<path\b",
            text
        )
    )

    polylines = len(
        re.findall(
            r"<polyline\b",
            text
        )
    )

    polygons = len(
        re.findall(
            r"<polygon\b",
            text
        )
    )

    results.append({

        "svg":
            str(svg),

        "paths":
            paths,

        "polylines":
            polylines,

        "polygons":
            polygons
    })

print()
print(
    f"SVGs: {len(results)}"
)

print()
print(
    json.dumps(
        results[:10],
        indent=2
    )
)
