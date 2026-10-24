import json

file = r"external\racing-track-maps-vector\from-iracing\Road\zandvoort\485-zandvoort-2023-gp\commentary.json"

data = json.load(
    open(
        file,
        encoding="utf-8"
    )
)

summary = data["track_summary"]

top = sorted(
    summary.items(),
    key=lambda x: x[1],
    reverse=True
)[:5]

data["top_characteristics"] = [
    x[0]
    for x in top
]

with open(
    file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        data,
        f,
        indent=2
    )

print("updated")
