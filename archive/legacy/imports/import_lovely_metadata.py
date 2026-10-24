from pathlib import Path
import json

COVERAGE_FILE = Path(
    "registry/lovely_coverage.json"
)

OUTPUT_ROOT = Path(
    "imports/lovely"
)

with open(
    COVERAGE_FILE,
    encoding="utf-8"
) as fp:

    coverage = json.load(fp)

imported = 0

for record in coverage.values():

    if not record["lovely_available"]:
        continue

    lovely_file = Path(
        record["lovely_file"]
    )

    with open(
        lovely_file,
        encoding="utf-8"
    ) as fp:

        src = json.load(fp)

    output = {

        "track_id":
            record["track_id"],

        "name":
            src.get("name"),

        "length_m":
            src.get("length"),

        "pit": {
            "entry_pct":
                src.get("pitentry"),

            "exit_pct":
                src.get("pitexit")
        },

        "sectors":
            src.get(
                "sector",
                []
            ),

        "corners": [
            {
                "name":
                    corner.get(
                        "name"
                    ),

                "start_pct":
                    corner.get(
                        "start"
                    ),

                "end_pct":
                    corner.get(
                        "end"
                    )
            }

            for corner
            in src.get(
                "turn",
                []
            )
        ]
    }

    output_path = (
        OUTPUT_ROOT
        / f"{record['track_id']}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            output,
            fp,
            indent=2
        )

    imported += 1

print(
    f"Imported {imported} tracks"
)
