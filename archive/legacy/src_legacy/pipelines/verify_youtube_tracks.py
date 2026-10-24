import json
from pathlib import Path

TRACK_MAP = {
    127: "Road Atlanta",
    219: "Bathurst",
    485: "Zandvoort",
    525: "Spa"
}

for track_id,name in TRACK_MAP.items():

    file = Path(
        f"generated/{track_id}.json"
    )

    if not file.exists():
        continue

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    print(
        name,
        len(
            data.get(
                "corners",
                []
            )
        )
    )
