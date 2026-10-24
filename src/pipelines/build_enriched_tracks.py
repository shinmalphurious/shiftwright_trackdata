from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = ROOT / "generated"
DEP_DIR = ROOT / "generated" / "corner_dependencies"
CHAR_DIR = ROOT / "generated" / "corner_characteristics"

OUT_DIR = ROOT / "generated" / "enriched_tracks"

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

for track_file in TRACK_DIR.glob("*.json"):

    if track_file.parent != TRACK_DIR:
        continue

    track_id = track_file.stem

    dep_file = DEP_DIR / f"{track_id}.json"
    char_file = CHAR_DIR / f"{track_id}.json"

    if (
        not dep_file.exists()
        or
        not char_file.exists()
    ):
        continue

    with open(
        track_file,
        "r",
        encoding="utf-8"
    ) as f:
        track = json.load(f)

    with open(
        dep_file,
        "r",
        encoding="utf-8"
    ) as f:
        deps = json.load(f)

    with open(
        char_file,
        "r",
        encoding="utf-8"
    ) as f:
        chars = json.load(f)

    named_corners = track.get(
        "corners",
        []
    )

    deps_list = deps.get(
        "dependencies",
        []
    )

    chars_list = chars.get(
        "corners",
        []
    )

    merged = []

    count = min(
        len(named_corners),
        len(deps_list),
        len(chars_list)
    )

    for i in range(count):

        corner = dict(
            named_corners[i]
        )

        corner[
            "exit_importance"
        ] = deps_list[i].get(
            "exit_importance"
        )

        corner[
            "dependency_reason"
        ] = deps_list[i].get(
            "reason"
        )

        corner[
            "corner_type"
        ] = chars_list[i].get(
            "classification"
        )

        merged.append(
            corner
        )

    track[
        "enriched_corners"
    ] = merged

    with open(
        OUT_DIR /
        track_file.name,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            track,
            f,
            indent=2
        )

print(
    "complete"
)
