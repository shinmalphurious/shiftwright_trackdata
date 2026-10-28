"""Official iRacing track and layout names, from racing-track-maps-vector's metadata.

The metadata file stores accented names double-encoded ("AutÃ³dromo" for "Autódromo"). Read
it only through this module, which repairs every text value; never read the file directly.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

from src.shared.paths import TRACK_MAPS
from src.shared.track_names import repair


YEAR = re.compile(r"^(19|20)\d\d$")
METADATA = TRACK_MAPS / "iracing-tracks-metadata.json"


def _repaired(value):
    if isinstance(value, str):
        return repair(value)
    if isinstance(value, list):
        return [_repaired(v) for v in value]
    if isinstance(value, dict):
        return {k: _repaired(v) for k, v in value.items()}
    return value


@lru_cache(maxsize=1)
def _raw_tracks():
    return json.loads(METADATA.read_text(encoding="utf-8-sig"))["tracks"]


@lru_cache(maxsize=1)
def load_venues():
    """The metadata's venue records (track_name, about_text, configurations, ...), repaired."""
    return [_repaired(track) for track in _raw_tracks()]


def venue_record(venue):
    """The repaired metadata record of a venue, or None."""
    return next((t for t in load_venues() if t["track_name"] == venue), None)


@lru_cache(maxsize=1)
def load_layouts():
    """track_id -> {name, venue, config, layout, is_oval, legacy, name_repaired}.

    name is iRacing's full name ("Circuit Park Zandvoort - Grand Prix - 2009"), venue the track
    it belongs to ("Circuit Zandvoort"), config the layout part ("Grand Prix"; empty for a
    single-layout track), legacy whether it is an older version of the venue. name_repaired
    is True when the metadata stored the name double-encoded.
    """
    layouts = {}
    for raw in _raw_tracks():
        venue = repair(raw["track_name"])
        for config in raw["configurations"]:
            stored = config.get("track_name_and_config") or raw["track_name"]
            full = repair(stored)
            parts = [p.strip() for p in full.split(" - ")]
            config_parts = [p for p in parts[1:] if not YEAR.match(p) and p != venue]
            layouts[config["track_id"]] = {
                "name": full,
                "venue": venue,
                "config": " - ".join(config_parts),
                "layout": Path(config.get("svg_local_path", "")).name,
                "is_oval": raw.get("is_oval", False),
                "legacy": "[legacy]" in full.lower() or any(YEAR.match(p) for p in parts),
                "name_repaired": full != stored or venue != raw["track_name"],
            }
    return layouts
