import json

lookup = json.load(
    open(
        "generated/vehicle_lookup.json",
        encoding="utf-8"
    )
)

tests = [

    "Track Guide | iRacing Rallycross at Daytona Short",

    "iRacing Fast Lap Guide | Pro Lite 2 Truck - Daytona Short",

    "It's NOT Just Luck! iRacing Daytona 500 Strategy Guide 2025"
]

for test in tests:

    found = None

    lower = test.lower()

    for alias,canonical in lookup.items():

        if alias in lower:

            found = canonical

            break

    print()
    print(test)
    print("->", found)
