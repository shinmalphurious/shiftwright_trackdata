from __future__ import annotations

import json
from pathlib import Path

from src.corners.corner_dependency import (
    calculate_exit_importance
)

ROOT = Path(__file__).resolve().parents[2]

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

OUTPUT_DIR = (
    ROOT /
    "generated" /
    "corner_dependencies"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def process_file(path: Path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    corners = data.get(
        "corners",
        []
    )

    output = {
        "track_id":
            data["track_id"],
        "dependencies": []
    }

    count = len(corners)

    for i, corner in enumerate(corners):

        next_corner = corners[
            (i + 1) % count
        ]

        straight_len = (
            next_corner["start_pct"]
            -
            corner["end_pct"]
        )

        if straight_len < 0:
            straight_len += 1.0

        output["dependencies"].append(
            {
                "corner_id": i + 1,

                "following_straight_pct":
                    round(
                        straight_len,
                        6
                    ),

                "exit_importance":
                    calculate_exit_importance(
                        straight_len
                    ),

                "reason":
                    "long_following_straight"
                    if straight_len > 0.08
                    else "normal"
            }
        )

    with open(
        OUTPUT_DIR / path.name,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        f"processed {path.name}"
    )


def main():

    files = sorted(
        REGION_DIR.glob("*.json")
    )

    for file in files:
        process_file(file)

    print(
        f"generated {len(files)} files"
    )


if __name__ == "__main__":
    main()
