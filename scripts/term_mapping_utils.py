import json
from pathlib import Path
from typing import Dict, Tuple


def normalize(s: str) -> str:
    return s.strip().lower()


def build_lookup(dictionary_path: Path) -> Tuple[Dict[str, str], Dict[str, int]]:
    """Build lookup maps from any token to canonical term and ID.

    Returns:
        token_to_canonical: maps any known alias/abbr/misspelling/canonical to canonical string
        canonical_to_id: maps canonical to its id
    """
    with dictionary_path.open(encoding='utf-8') as f:
        data = json.load(f)

    token_to_canonical: Dict[str, str] = {}
    canonical_to_id: Dict[str, int] = {}

    for entry in data:
        cid = int(entry["id"])
        canonical = normalize(entry["canonical"])  # already lower in generator, but normalize again
        canonical_to_id[canonical] = cid

        def add(token: str):
            token_to_canonical[normalize(token)] = canonical

        # include canonical itself
        add(canonical)
        for s in entry.get("synonyms", []) or []:
            add(s)
        for s in entry.get("abbreviations", []) or []:
            add(s)
        for s in entry.get("misspellings", []) or []:
            add(s)

    return token_to_canonical, canonical_to_id


def map_input(text: str, token_to_canonical: Dict[str, str]):
    return token_to_canonical.get(normalize(text))
