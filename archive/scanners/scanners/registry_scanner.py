from __future__ import annotations

import json
import re
from pathlib import Path


TRACK_PATTERN = re.compile(
    r"^(?P<track_id>\d+)-(?P<remainder>.+)$"
)


TRACK_MAPS_ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector"
)

REPO_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
ELEVATION_ROOT = REPO_ROOT / "elevation"

REGISTRY_ROOT = REPO_ROOT / "registry"
REGISTRY_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


def discover_layouts():
    """
    Discover folders matching:

    403-spielberg-gp
    123-road-atlanta-full
    """

    for path in TRACK_MAPS_ROOT.rglob("*"):

        if not path.is_dir():
            continue

        match = TRACK_PATTERN.match(path.name)

        if match:
            yield path, match


def discover_assets(track_dir: Path) -> dict:

    files = {
        file.name.lower()
        for file in track_dir.iterdir()
        if file.is_file()
    }

    return {
        "active_svg": "active.svg" in files,
        "pitroad_svg": "pitroad.svg" in files,
        "startfinish_svg": "startfinish.svg" in files,
        "sectors_svg": "sectors.svg" in files
    }


def build_layout_entry(track_dir: Path, match) -> dict:

    track_id = int(
        match.group("track_id")
    )

    folder_name = track_dir.name

    pieces = folder_name.split("-")

    venue_slug = None
    layout_slug = None

    if len(pieces) >= 2:
        venue_slug = pieces[1]

    if len(pieces) >= 3:
        layout_slug = "-".join(
            pieces[2:]
        )

    knowledge_dir = (
        KNOWLEDGE_ROOT
        / str(track_id)
    )

    elevation_dir = (
        ELEVATION_ROOT
        / str(track_id)
    )

    return {
        "track_id": track_id,
        "folder_name": folder_name,
        "venue_slug": venue_slug,
        "layout_slug": layout_slug,

        "assets": discover_assets(
            track_dir
        ),

        "coverage": {
            "knowledge": knowledge_dir.exists(),
            "elevation": elevation_dir.exists()
        }
    }


def main():

    tracks = {}

    missing_knowledge = set()
    missing_elevation = set()

    layout_count = 0

    for track_dir, match in discover_layouts():

        layout = build_layout_entry(
            track_dir,
            match
        )

        track_id = str(
            layout["track_id"]
        )

        tracks.setdefault(
            track_id,
            []
        )

        tracks[track_id].append(
            layout
        )

        layout_count += 1

        if not layout["coverage"]["knowledge"]:
            missing_knowledge.add(
                layout["track_id"]
            )

        if not layout["coverage"]["elevation"]:
            missing_elevation.add(
                layout["track_id"]
            )

    sorted_tracks = dict(
        sorted(
            tracks.items(),
            key=lambda x: int(x[0])
        )
    )

    coverage = {}

    for track_id, layouts in sorted_tracks.items():

        coverage[track_id] = {
            "knowledge": any(
                layout["coverage"]["knowledge"]
                for layout in layouts
            ),

            "elevation": any(
                layout["coverage"]["elevation"]
                for layout in layouts
            ),

            "layout_count": len(
                layouts
            )
        }

    missing_assets = {
        "missing_knowledge": sorted(
            missing_knowledge
        ),
        "missing_elevation": sorted(
            missing_elevation
        )
    }

    with open(
        REGISTRY_ROOT / "tracks.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            sorted_tracks,
            f,
            indent=2
        )

    with open(
        REGISTRY_ROOT / "coverage.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            coverage,
            f,
            indent=2
        )

    with open(
        REGISTRY_ROOT / "missing_assets.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            missing_assets,
            f,
            indent=2
        )

    print()
    print("Registry generated")
    print(
        f"Tracks discovered : {len(sorted_tracks)}"
    )
    print(
        f"Layouts discovered: {layout_count}"
    )
    print(
        f"Output directory  : {REGISTRY_ROOT}"
    )


if __name__ == "__main__":
    main()
