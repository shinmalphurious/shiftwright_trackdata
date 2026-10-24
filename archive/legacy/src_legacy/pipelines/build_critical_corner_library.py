from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    ROOT /
    "generated" /
    "corner_dependencies"
)

OUTPUT_DIR = (
    ROOT /
    "generated" /
    "critical_corners"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

for file in INPUT_DIR.glob(
    "*.json"
):

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    deps = sorted(
        data["dependencies"],
        key=lambda x:
        x["exit_importance"],
        reverse=True
    )

    selected = deps[:3]

    with open(
        OUTPUT_DIR / file.name,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "track_id":
                    data["track_id"],

                "critical_corners":
                    selected
            },
            f,
            indent=2
        )

print(
    "complete"
)
