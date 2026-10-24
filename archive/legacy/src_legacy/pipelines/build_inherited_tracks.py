from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = ROOT / "generated"

OUTPUT_DIR = (
    ROOT /
    "generated" /
    "inherited_tracks"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CANDIDATES = [
    (486,485),
    (503,501),
    (29,192),
    (148,485),
    (194,192),
    (504,501),
    (510,509)
]

for child_id,parent_id in CANDIDATES:

    child_file = (
        TRACK_DIR /
        f"{child_id}.json"
    )

    parent_file = (
        TRACK_DIR /
        f"{parent_id}.json"
    )

    if (
        not child_file.exists()
        or
        not parent_file.exists()
    ):
        continue

    with open(
        child_file,
        "r",
        encoding="utf-8"
    ) as f:
        child = json.load(f)

    with open(
        parent_file,
        "r",
        encoding="utf-8"
    ) as f:
        parent = json.load(f)

    child[
        "inherited_corner_knowledge"
    ] = {
        "parent_track_id":
            parent_id,

        "parent_corner_count":
            len(
                parent.get(
                    "corners",
                    []
                )
            ),

        "corner_names":
            [
                c["name"]
                for c in parent.get(
                    "corners",
                    []
                )
            ]
    }

    with open(
        OUTPUT_DIR /
        f"{child_id}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            child,
            f,
            indent=2
        )

print(
    "complete"
)
