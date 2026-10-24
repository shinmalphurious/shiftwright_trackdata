import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

import json

from src.corners.corner_classifier import (
    classify_corner
)

INPUT_DIR = Path(
    "generated/corner_regions"
)

OUTPUT_DIR = Path(
    "generated/corner_classifications"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for file in INPUT_DIR.glob(
    "*.json"
):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    output = {

        "track_id":
            data["track_id"],

        "source":
            "generated",

        "corners":
            []
    }

    for idx, corner in enumerate(
        data["corners"],
        start=1
    ):

        width_pct = (
            corner["end_pct"]
            -
            corner["start_pct"]
        )

        classification = classify_corner(
            corner["strength"],
            width_pct
        )

        output[
            "corners"
        ].append({

            "corner_id":
                idx,

            "start_pct":
                corner["start_pct"],

            "apex_pct":
                corner["apex_pct"],

            "end_pct":
                corner["end_pct"],

            "strength":
                corner["strength"],

            "classification":
                classification
        })

    with open(
        OUTPUT_DIR /
        file.name,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            output,
            fp,
            indent=2
        )

    built += 1

print()
print(
    f"Built: {built}"
)
