from __future__ import annotations

import json
from pathlib import Path

from src.corners.characteristics import (
    classify_corner,
    calculate_severity,
)


ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = ROOT / "generated" / "corner_metrics"

OUTPUT_DIR = ROOT / "generated" / "corner_characteristics"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def process_file(path: Path):

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = {
        "track_id": data["track_id"],
        "source": "generated",
        "corners": []
    }

    for idx, corner in enumerate(
        data.get("corners", []),
        start=1
    ):

        angle = corner.get(
            "angle_deg",
            0.0
        )

        strength = corner.get(
            "strength",
            0.0
        )

        severity = calculate_severity(
            angle,
            strength
        )

        output["corners"].append(
            {
                "corner_id": idx,

                "start_pct":
                    corner["start_pct"],

                "apex_pct":
                    corner["apex_pct"],

                "end_pct":
                    corner["end_pct"],

                "strength":
                    strength,

                "width_pct":
                    corner["width_pct"],

                "angle_deg":
                    angle,

                "severity":
                    severity,

                "classification":
                    classify_corner(angle)
            }
        )

    out_file = (
        OUTPUT_DIR /
        path.name
    )

    with open(
        out_file,
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
        INPUT_DIR.glob("*.json")
    )

    for file in files:
        process_file(file)

    print(
        f"generated {len(files)} files"
    )


if __name__ == "__main__":
    main()
