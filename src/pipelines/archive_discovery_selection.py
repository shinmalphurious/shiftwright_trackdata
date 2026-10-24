import json
from pathlib import Path

selection = json.load(
    open(
        "generated/discovery_selection.json",
        encoding="utf-8"
    )
)

catalog_dir = Path(
    "generated/guide_catalog"
)

catalog_dir.mkdir(
    parents=True,
    exist_ok=True
)

track_id = selection[
    "track_id"
]

outfile = (
    catalog_dir /
    f"{track_id}.json"
)

with open(
    outfile,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        selection,
        fp,
        indent=2
    )

print(
    outfile.name
)
