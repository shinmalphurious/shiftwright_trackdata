import json
from pathlib import Path


def main():
    path = Path("generated/discovery_effectiveness.json")

    if not path.exists():
        print("missing: generated/discovery_effectiveness.json")
        return

    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)

    data.sort(
        key=lambda x: (
            x.get("cars", 0) * x.get("guides", 0),
            x.get("cars", 0),
            x.get("guides", 0)
        ),
        reverse=True
    )

    print()
    print("=" * 80)
    print("TOP DISCOVERY PRIORITIES")
    print("=" * 80)
    print()

    for row in data[:25]:
        score = row.get("cars", 0) * row.get("guides", 0)

        print(
            f"{row['track_id']:>4} "
            f"{row['layout']:<45} "
            f"cars={row['cars']:<3} "
            f"guides={row['guides']:<3} "
            f"priority={score}"
        )

    print()
    print(f"tracks analysed: {len(data)}")


if __name__ == "__main__":
    main()