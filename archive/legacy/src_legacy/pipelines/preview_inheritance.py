from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = ROOT / "generated"

CANDIDATES = [
    (29,192),
    (42,341),
    (148,485),
    (194,192),
    (240,239),
    (246,239),
    (343,341),
    (486,485),
    (503,501),
    (504,501),
    (510,509),
]

for child_id,parent_id in CANDIDATES:

    parent_file = TRACK_DIR / f"{parent_id}.json"

    if not parent_file.exists():
        continue

    with open(
        parent_file,
        "r",
        encoding="utf-8"
    ) as f:
        parent = json.load(f)

    corners = parent.get(
        "corners",
        []
    )

    print()
    print(
        f"{child_id} <- {parent_id}"
    )

    print(
        f"parent corners: {len(corners)}"
    )

    for corner in corners[:5]:

        print(
            "  "
            + corner["name"]
        )
