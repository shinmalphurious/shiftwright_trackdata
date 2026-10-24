from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LOVELY_DIR = Path(
    r"E:\Project_Shiftwright\external\lovely-track-data\data\iracing"
)

for path in sorted(LOVELY_DIR.glob("*.json")):

    try:

        with open(path,"r",encoding="utf-8") as f:
            data = json.load(f)

        print(
            f"{data.get('trackId')} | {path.stem}"
        )

    except Exception as e:

        print(
            f"ERROR {path.name} {e}"
        )
