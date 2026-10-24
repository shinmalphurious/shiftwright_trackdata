import json
from pathlib import Path

from src.corners.apex_merger import (
    merge_apexes
)

APEX_DIR = Path(
    "generated/corner_apexes"
)

for file in APEX_DIR.glob(
    "*.json"
):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    merged = merge_apexes(
        data["apexes"]
    )

    if file.stem == "403":

        print()

        print(
            f"Original: "
            f"{len(data['apexes'])}"
        )

        print(
            f"Merged: "
            f"{len(merged)}"
        )

        print()

        for apex in merged:

            print(
                apex
            )
