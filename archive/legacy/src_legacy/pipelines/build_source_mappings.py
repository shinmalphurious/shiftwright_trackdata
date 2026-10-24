from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

TRACKS_FILE = ROOT / "registry" / "tracks.json"

LOVELY_DIR = Path(
    r"E:\Project_Shiftwright\external\lovely-track-data\data\iracing"
)

OUTPUT_FILE = (
    ROOT /
    "registry" /
    "source_mappings.json"
)


def load_tracks():

    with open(
        TRACKS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def load_lovely_ids():

    mappings = {}

    for path in LOVELY_DIR.glob("*.json"):

        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            track_id = data.get(
                "trackId"
            )

            if track_id:
                mappings[track_id] = path.name

        except Exception:
            pass

    return mappings


def main():

    tracks = load_tracks()

    lovely = load_lovely_ids()

    output = {}

    matched = 0

    for track_id, entries in tracks.items():

        for entry in entries:

            venue_slug = entry.get(
                "venue_slug"
            )

            layout_slug = entry.get(
                "layout_slug"
            )

            lovely_track = None

            if venue_slug in lovely:
                lovely_track = venue_slug
                matched += 1

            output[track_id] = {
                "track_id":
                    int(track_id),

                "venue_slug":
                    venue_slug,

                "layout_slug":
                    layout_slug,

                "lovely_track_id":
                    lovely_track
            }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        f"mapped {matched} tracks"
    )

    print(
        f"wrote {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
