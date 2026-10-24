from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

LOVELY_DIR = Path(
    r"E:\Project_Shiftwright\external\lovely-track-data\data\iracing"
)

CHAR_DIR = (
    ROOT /
    "generated" /
    "corner_characteristics"
)

OUT_DIR = (
    ROOT /
    "generated" /
    "lovely_alignment"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def nearest_corner(
    lovely_apex,
    generated
):
    best = None
    best_offset = 999

    for corner in generated:

        offset = abs(
            corner["apex_pct"] -
            lovely_apex
        )

        if offset < best_offset:
            best_offset = offset
            best = corner

    return best, best_offset


def confidence(offset_pct):

    return round(
        max(
            0.0,
            1.0 - offset_pct / 0.05
        ),
        4,
    )


def process_file(path: Path):

    stem = path.stem

    generated_file = (
        CHAR_DIR /
        f"{stem}.json"
    )

    if not generated_file.exists():
        return

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        lovely = json.load(f)

    with open(
        generated_file,
        "r",
        encoding="utf-8"
    ) as f:
        generated = json.load(f)

    output = {
        "track_id":
            generated["track_id"],

        "track_name":
            lovely["name"],

        "matches": []
    }

    for turn in lovely.get(
        "turn",
        []
    ):

        lovely_apex = (
            turn["start"] +
            turn["end"]
        ) / 2

        corner, offset = nearest_corner(
            lovely_apex,
            generated["corners"]
        )

        output["matches"].append(
            {
                "lovely_name":
                    turn["name"],

                "lovely_apex":
                    round(
                        lovely_apex,
                        6
                    ),

                "generated_corner_id":
                    corner["corner_id"],

                "generated_apex":
                    corner["apex_pct"],

                "offset_pct":
                    round(
                        offset,
                        6
                    ),

                "confidence":
                    confidence(offset)
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


def main():

    files = sorted(
        LOVELY_DIR.glob("*.json")
    )

    processed = 0

    for file in files:
        process_file(file)
        processed += 1

    print(
        f"processed {processed} lovely files"
    )


if __name__ == "__main__":
    main()
