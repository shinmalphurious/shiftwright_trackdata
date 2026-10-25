"""Single place for filesystem locations.

External datasets live in one shared root for the whole Shiftwright ecosystem.
Set SHIFTWRIGHT_DATA_ROOT to override; the default is the platform repo's
external/ folder next to this repo.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED = REPO_ROOT / "generated"

DATA_ROOT = Path(
    os.environ.get("SHIFTWRIGHT_DATA_ROOT")
    or REPO_ROOT.parent / "Project_Shiftwright" / "external"
)

TRACK_MAPS = DATA_ROOT / "racing-track-maps-vector" / "from-iracing"
LOVELY_CARS = DATA_ROOT / "lovely-car-data" / "data" / "iracing"
