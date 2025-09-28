import csv
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NEW_DIR = ROOT / "data" / "new"
OLD_DIR = ROOT / "data" / "old"
CLASS_MAPPING_CSV = NEW_DIR / "class_mapping.csv"
OLD_DICTIONARY_JSON = OLD_DIR / "derm_dictionary.json"
OUTPUT_JSON = NEW_DIR / "derm_dictionary.json"


def load_class_mapping(path: Path):
    items = []
    # Use utf-8-sig to safely handle BOM in CSV headers
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                class_id = int(row["class_id"])  # type: ignore
            except (KeyError, ValueError):
                continue
            disease = (row.get("disease_condition") or "").strip()
            if not disease:
                continue
            items.append({"id": class_id, "canonical": disease})
    return items


def load_old_dictionary(path: Path):
    if not path.exists():
        return {}
    with path.open(encoding='utf-8') as f:
        data = json.load(f)
    by_canonical = {}
    for entry in data:
        can = (entry.get("canonical") or "").strip().lower()
        if not can:
            continue
        by_canonical[can] = {
            "synonyms": [s.strip().lower() for s in entry.get("synonyms", []) if isinstance(s, str)],
            "abbreviations": [s.strip() for s in entry.get("abbreviations", []) if isinstance(s, str)],
        }
    return by_canonical


def unique_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        if not x:
            continue
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def brit_american_variants(term: str):
    # Generate British/American spelling variants where common in derm terms
    variants = set()
    t = term
    variants.add(t)
    # hemangioma/haemangioma
    if "hemangioma" in t:
        variants.add(t.replace("hemangioma", "haemangioma"))
    if "haemangioma" in t:
        variants.add(t.replace("haemangioma", "hemangioma"))
    # seborrheic/seborrhoeic
    if "seborrheic" in t:
        variants.add(t.replace("seborrheic", "seborrhoeic"))
    if "seborrhoeic" in t:
        variants.add(t.replace("seborrhoeic", "seborrheic"))
    # nevus/naevus (and related compound terms)
    if "nevus" in t:
        variants.add(t.replace("nevus", "naevus"))
    if "naevus" in t:
        variants.add(t.replace("naevus", "nevus"))
    return {v for v in variants if v}


def hyphen_space_variants(term: str):
    variants = set()
    variants.add(term)
    # hyphenate palmo plantar, kerato acanthoma, etc.
    variants.add(term.replace(" ", "-"))
    variants.add(term.replace("-", " "))
    # remove apostrophes
    variants.add(term.replace("'", ""))
    return {v for v in variants if v}


def possessive_variants(term: str):
    variants = set()
    variants.add(term)
    # Bowen disease -> Bowen's disease
    if re.search(r"\b([A-Za-z]+) disease\b", term):
        variants.add(re.sub(r"\b([A-Za-z]+) disease\b", r"\1's disease", term))
    return variants


CURATED_ABBREVIATIONS = {
    "actinic keratosis": ["AK"],
    "basal cell carcinoma": ["BCC"],
    "squamous cell carcinoma": ["SCC"],
    "herpes simplex": ["HSV"],
    "herpes zoster": ["HZ"],
    "alopecia areata": ["AA"],
    "pityriasis lichenoides et varioliformis acuta": ["PLEVA"],
    "pityriasis lichenoides chronica": ["PLC"],
    "keratosis pilaris": ["KP"],
    "molluscum contagiosum": ["MC"],
    "juvenile xanthogranuloma": ["JXG"],
    "palmoplantar pustulosis": ["PPP"],
    "staphylococcal scalded skin syndrome": ["SSSS"],
    "erythema multiforme": ["EM"],
}


CURATED_SYNONYMS = {
    "tinea versicolor": ["pityriasis versicolor"],
    "tinea cruris": ["dhobi itch", "groin tinea", "jock itch", "tinea inguinalis"],
    "herpes zoster": ["shingles"],
    "pyogenic granuloma": ["lobular capillary haemangioma", "lobular capillary hemangioma"],
    "actinic keratosis": ["solar keratosis"],
    "onychomycosis": ["tinea unguium"],
    "bowen disease": ["bowen's disease"],
}


CURATED_MISSPELLINGS = {
    "folliculitis": ["foliculitis"],
    "cellulitis": ["cellulitus"],
    "erythema multiforme": ["erythema multiform"],
    "keratoacanthoma": ["keratocanthoma", "kerato acanthoma", "kerato-acanthoma"],
    "palmoplantar pustulosis": ["palmo plantar pustulosis", "palmo-plantar pustulosis"],
    "inflammed cyst": ["inflamed cyst"],
    "seborrheic dermatitis": ["seborrhoeic dermatitis"],
    "seborrheic keratosis": ["seborrhoeic keratosis"],
    "hemangioma": ["haemangioma"],
}


def build_entry(item, old_map):
    cid = item["id"]
    canonical_src = item["canonical"].strip()
    canonical = canonical_src.lower()

    synonyms = []
    abbreviations = []
    misspellings = []

    # From old dictionary if canonical matches
    if canonical in old_map:
        synonyms.extend(old_map[canonical].get("synonyms", []))
        abbreviations.extend(old_map[canonical].get("abbreviations", []))

    # Curated adds
    synonyms.extend(CURATED_SYNONYMS.get(canonical, []))
    abbreviations.extend(CURATED_ABBREVIATIONS.get(canonical, []))
    misspellings.extend(CURATED_MISSPELLINGS.get(canonical, []))

    # Algorithmic variants (as synonyms, not misspellings)
    algo_vars = set()
    for v in brit_american_variants(canonical):
        algo_vars.add(v)
    for v in hyphen_space_variants(canonical):
        algo_vars.add(v)
    for v in possessive_variants(canonical):
        algo_vars.add(v)

    # Remove canonical itself
    if canonical in algo_vars:
        algo_vars.remove(canonical)
    synonyms.extend(sorted(algo_vars))

    # Normalize lists
    synonyms = [s.strip().lower() for s in synonyms if isinstance(s, str)]
    abbreviations = [s.strip() for s in abbreviations if isinstance(s, str)]
    misspellings = [s.strip().lower() for s in misspellings if isinstance(s, str)]

    # Deduplicate and ensure canonical not inside
    synonyms = [s for s in unique_preserve(synonyms) if s != canonical]
    abbreviations = unique_preserve(abbreviations)
    misspellings = [s for s in unique_preserve(misspellings) if s != canonical]

    return {
        "id": cid,
        "canonical": canonical,
        "synonyms": synonyms,
        "abbreviations": abbreviations,
        "misspellings": misspellings,
    }


def main():
    assert CLASS_MAPPING_CSV.exists(), f"Missing {CLASS_MAPPING_CSV}"
    items = load_class_mapping(CLASS_MAPPING_CSV)
    old_map = load_old_dictionary(OLD_DICTIONARY_JSON)

    entries = []
    for it in items:
        entries.append(build_entry(it, old_map))

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open('w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(entries)} entries to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
