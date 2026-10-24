import json

aliases = json.load(
    open(
        "data/vehicle_aliases.json",
        encoding="utf-8"
    )
)

lookup = {}

for canonical,names in aliases.items():

    for name in names:

        lookup[
            name.lower()
        ] = canonical

with open(
    "generated/vehicle_lookup.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        lookup,
        fp,
        indent=2
    )

print(
    "aliases:",
    len(lookup)
)
