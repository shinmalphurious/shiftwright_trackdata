import json

track = json.load(
    open(
        "generated/485.json",
        encoding="utf-8"
    )
)

for i,corner in enumerate(
    track["corners"],
    start=1
):

    corner["corner_index"] = i

with open(
    "generated/485_numbered.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        track,
        f,
        indent=2
    )

print("done")
