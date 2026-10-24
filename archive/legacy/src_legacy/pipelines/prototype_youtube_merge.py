import json
from pathlib import Path

track = json.load(
    open(
        "generated/485.json",
        encoding="utf-8"
    )
)

youtube_knowledge = [
    {
        "turn": 10,
        "facts": [
            "slippery",
            "cambered",
            "early_throttle"
        ]
    }
]

for corner in track["corners"]:

    corner["youtube_facts"] = []

# TEMPORARY MANUAL MAPPING
track["corners"][9]["youtube_facts"] = [
    "slippery",
    "cambered",
    "early_throttle"
]

with open(
    "generated/485_enriched_youtube.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        track,
        f,
        indent=2
    )

print("merged")
