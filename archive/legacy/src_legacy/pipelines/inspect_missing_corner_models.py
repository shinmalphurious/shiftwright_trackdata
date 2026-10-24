import json

catalog = {
    t["track_id"]: t
    for t in json.load(
        open(
            "generated/track_catalog.json",
            encoding="utf-8"
        )
    )
}

missing = json.load(
    open(
        "generated/missing_corner_models.json",
        encoding="utf-8"
    )
)

print()

for track_id in missing[:100]:

    print(
        track_id,
        catalog[track_id]["layout"]
    )

print()
print(
    "shown:",
    min(100, len(missing))
)
print(
    "total:",
    len(missing)
)
