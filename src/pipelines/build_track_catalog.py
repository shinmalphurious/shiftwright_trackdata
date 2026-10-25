import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared.paths import GENERATED, TRACK_MAPS

tracks = []

for turns_svg in TRACK_MAPS.rglob("turns.svg"):
    folder = turns_svg.parent
    try:
        track_id = int(folder.name.split("-")[0])
    except ValueError:
        continue
    tracks.append({
        "track_id": track_id,
        "layout": folder.name,
        "layout_path": folder.relative_to(TRACK_MAPS).as_posix(),
        "has_active_svg": (folder / "active.svg").exists(),
        "has_turns_svg": True,
        "has_commentary": (folder / "commentary.json").exists(),
    })

tracks.sort(key=lambda x: x["track_id"])

(GENERATED / "track_catalog.json").write_text(json.dumps(tracks, indent=2), encoding="utf-8")

print("tracks:", len(tracks))
