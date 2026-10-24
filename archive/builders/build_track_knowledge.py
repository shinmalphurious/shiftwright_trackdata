import json
from pathlib import Path

SOURCE_COVERAGE = Path(
    "registry/source_coverage.json"
)

LOVELY_DIR = Path(
    "imports/lovely"
)

OUTPUT_DIR = Path(
    "generated"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)

with open(
    SOURCE_COVERAGE,
    encoding="utf-8"
) as fp:

    coverage = json.load(fp)

generated = 0

for track_id, track_sources in coverage.items():

    knowledge = {

        "track_id": int(track_id),

        "source_coverage":
            track_sources,

        "metadata": {},

        "pit": {},

        "sectors": [],

        "corners": []
    }

    lovely_file = (
        LOVELY_DIR
        / f"{track_id}.json"
    )

    if lovely_file.exists():

        with open(
            lovely_file,
            encoding="utf-8"
        ) as fp:

            lovely = json.load(fp)

        knowledge["metadata"] = {

            "name":
                lovely.get("name"),

            "length_m":
                lovely.get("length_m")
        }

        knowledge["pit"] = (
            lovely.get("pit", {})
        )

        knowledge["sectors"] = (
            lovely.get("sectors", [])
        )

        knowledge["corners"] = (
            lovely.get("corners", [])
        )

    with open(
        OUTPUT_DIR / f"{track_id}.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            knowledge,
            fp,
            indent=2
        )

    generated += 1

print(
    f"Generated {generated} track knowledge files"
)
