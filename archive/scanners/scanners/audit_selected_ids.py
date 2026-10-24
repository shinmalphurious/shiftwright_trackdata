import json

with open(
    "registry/lovely_coverage.json",
    encoding="utf-8"
) as fp:
    coverage = json.load(fp)

interesting = [
    161,162,169,170,171,172,173,174,
    175,176,178,182,188,189,190,191,
    193,194,201,203,204,205,206,213,
    214,215,216,217
]

for track_id in interesting:

    record = coverage.get(
        str(track_id)
    )

    if record:
        print(
            track_id,
            record["lovely_available"],
            record["lovely_slug"]
        )
