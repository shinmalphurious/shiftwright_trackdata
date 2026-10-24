from pathlib import Path

count = 0

for file in Path(
    "generated"
).glob("*.json"):

    try:

        track_id = int(
            file.stem
        )

        print(track_id)

        count += 1

    except:
        pass

print()
print(
    "track models:",
    count
)
