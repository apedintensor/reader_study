from pathlib import Path
from term_mapping_utils import build_lookup, map_input


def main():
    root = Path(__file__).resolve().parents[1]
    dictionary = root / "data" / "new" / "derm_dictionary.json"
    token_to_canonical, canonical_to_id = build_lookup(dictionary)

    samples = [
        "AK",
        "seborrhoeic keratosis",
        "bowen's disease",
        "kerato acanthoma",
        "haemangioma",
        "HSV",
        "tinea inguinalis",
        "palmo-plantar pustulosis",
        "inflamed cyst",
        "Seborrheic Dermatitis",
    ]

    for s in samples:
        mapped = map_input(s, token_to_canonical)
        print(f"{s!r} -> {mapped!r}  (id={canonical_to_id.get(mapped) if mapped else None})")


if __name__ == "__main__":
    main()
