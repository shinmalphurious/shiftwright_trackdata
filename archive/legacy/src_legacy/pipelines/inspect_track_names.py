import json
from pathlib import Path

for file in Path("generated").glob("*.json"):

    try:

        data = json.load(
            open(
                file,
                encoding="utf-8"
            )
        )

        corners = len(
            data.get(
                "corners",
                []
            )
        )

        if corners:

            print(
                file.stem,
                "|",
                data.get(
                    "track_name",
                    "UNKNOWN"
                ),
                "|",
                corners
            )

    except Exception:
        pass
