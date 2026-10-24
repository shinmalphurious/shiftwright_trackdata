import json

with open(
    "generated/axis_registry.json",
    encoding="utf-8"
) as fp:

    data = json.load(fp)

counts = [
    v["point_count"]
    for v in data.values()
]

print()

print(
    f"Tracks: {len(counts)}"
)

print(
    f"Min Points: {min(counts)}"
)

print(
    f"Max Points: {max(counts)}"
)

print(
    f"Average Points: "
    f"{sum(counts)/len(counts):.1f}"
)
