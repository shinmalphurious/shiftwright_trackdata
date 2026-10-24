from __future__ import annotations

import json
from pathlib import Path

from src.corners.corner_context import (
    classify_context
)

ROOT = Path(__file__).resolve().parents[2]

REGION_DIR = ROOT / "generated" / "corner_regions"

DEP_DIR = ROOT / "generated" / "corner_dependencies"

OUT_DIR = ROOT / "generated" / "corner_context"

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def process_file(path: Path):

    with open(path,"r",encoding="utf-8") as f:
        regions = json.load(f)

    with open(
        DEP_DIR / path.name,
        "r",
        encoding="utf-8"
    ) as f:
        deps = json.load(f)

    corners = regions["corners"]

    output = {
        "track_id":
            regions["track_id"],
        "corners": []
    }

    count = len(corners)

    for i, corner in enumerate(corners):

        next_corner = corners[
            (i + 1) % count
        ]

        gap = (
            next_corner["start_pct"]
            -
            corner["end_pct"]
        )

        if gap < 0:
            gap += 1.0

        dep = deps["dependencies"][i]

        output["corners"].append(
            {
                "corner_id":
                    i + 1,

                "gap_pct":
                    round(
                        gap,
                        6
                    ),

                "part_of_complex":
                    gap < 0.04,

                "role":
                    classify_context(
                        dep[
                            "following_straight_pct"
                        ],
                        gap
                    )
            }
        )

    with open(
        OUT_DIR / path.name,
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
