from pathlib import Path
import json
import re

REGISTRY_FILE = Path(
    "registry/tracks.json"
)

LOVELY_ROOT = Path(
    r"E:\Project_Shiftwright\external\lovely-track-data\data\iracing"
)

OUTPUT_FILE = Path(
    "registry/lovely_coverage.json"
)


def load_registry():

    with open(
        REGISTRY_FILE,
        encoding="utf-8"
    ) as fp:

        return json.load(fp)


def build_lovely_index():

    index = {}

    for file in LOVELY_ROOT.glob("*.json"):

        slug = file.stem.lower()

        index[slug] = str(file)

    return index


def extract_candidate_slugs(layout):

    folder_name = layout["folder_name"]

    match = re.match(
        r"^\d+-(.+)$",
        folder_name
    )

    if not match:
        return []

    remainder = match.group(1)

    candidates = {
        remainder.lower()
    }

    return list(candidates)


registry = load_registry()
lovely_index = build_lovely_index()

coverage = {}

matched = 0
unmatched = 0

for track_id, layouts in registry.items():

    layout = layouts[0]

    candidates = extract_candidate_slugs(
        layout
    )

    lovely_match = None

    for candidate in candidates:

        if candidate in lovely_index:

            lovely_match = (
                candidate
            )
            break

    coverage[track_id] = {

        "track_id": int(
            track_id
        ),

        "lovely_available":
            lovely_match is not None,

        "lovely_slug":
            lovely_match,

        "lovely_file":
            lovely_index.get(
                lovely_match
            )
            if lovely_match
            else None
    }

    if lovely_match:
        matched += 1
    else:
        unmatched += 1

OUTPUT_FILE.parent.mkdir(
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        coverage,
        fp,
        indent=2
    )

print()
print(
    f"Matched   : {matched}"
)
print(
    f"Unmatched : {unmatched}"
)
print()
print(
    f"Wrote {OUTPUT_FILE}"
)
