import json

with open(
    "registry/tracks.json",
    encoding="utf-8"
) as fp:
    tracks = json.load(fp)

interesting = [
161,162,169,170,171,172,173,174,
175,176,178,182,188,189,190,191,
193,194,201,203,204,205,206,213,
214,215,216,217
]

for track_id in interesting:

    layouts = tracks.get(
        str(track_id),
        []
    )

    if not layouts:
        continue

    print()
    print(f"TRACK {track_id}")
    print(
        json.dumps(
            layouts[0],
            indent=2
        )
    )
