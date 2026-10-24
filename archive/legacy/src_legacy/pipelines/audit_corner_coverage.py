from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)


def main():

    files = sorted(
        INPUT_DIR.glob("*.json")
    )

    for file in files:

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        total = 0.0

        for corner in data[
            "corners"
        ]:

            start = corner[
                "start_pct"
            ]

            end = corner[
                "end_pct"
            ]

            width = end - start

            if width < 0:
                width += 1.0

            total += width

        print(
            f'{data["track_id"]},'
            f'{len(data["corners"])},'
            f'{total:.3f}'
        )


if __name__ == "__main__":
    main()
