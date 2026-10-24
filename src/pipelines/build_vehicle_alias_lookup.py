import json
from pathlib import Path

index = json.load(
    open(
        "generated/iracing_vehicle_index.json",
        encoding="utf-8"
    )
)

aliases = {}

for vehicle in index:

    name = (
        vehicle.get(
            "carName"
        ) or ""
    ).lower()

    car_class = (
        vehicle.get(
            "carClass"
        ) or ""
    )

    aliases[name] = car_class

with open(
    "generated/vehicle_alias_lookup.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        aliases,
        fp,
        indent=2
    )

print(
    "aliases:",
    len(aliases)
)
