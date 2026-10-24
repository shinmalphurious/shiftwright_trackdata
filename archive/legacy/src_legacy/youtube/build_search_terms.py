import json
from pathlib import Path

ROOT = Path.cwd()

with open(
    ROOT / "generated" / "knowledge_registry.json",
    encoding="utf-8"
) as f:
    registry = json.load(f)

with open(
    ROOT / "research" / "youtube" / "catalog" / "search_terms.csv",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "track_id,search_term\n"
    )

    for track in registry:

        track_id = track["track_id"]

        f.write(
            f'{track_id},"iRacing track guide"\n'
        )

print(
    f"generated {len(registry)} searches"
)
