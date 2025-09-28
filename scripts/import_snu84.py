"""Import SNU84 CSV into DB and load terms/synonyms from new derm dictionary.

Usage (from backend/):
  python scripts/import_snu84.py \
    --terms data/new/derm_dictionary.json \
    --cases data/new/SNU84_sample_10_stratified_cleaned.csv

This expects:
  - terms JSON: list of {id, canonical, synonyms, abbreviations}
  - SNU84 CSV header with: image_path, gt, gt_disease, and many prob_class_<slug> columns

We infer class_id per probability column by matching <slug> to slugified canonical terms.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import models as m


def log(msg: str):
    print(f"[import_snu84] {msg}")


def slugify(s: str) -> str:
    return (
        s.strip()
        .lower()
        .replace("'", "")
        .replace("/", " ")
        .replace(" ", "_")
        .replace("-", "_")
    )


def load_terms_from_json(db: Session, path: Path) -> Tuple[int, int, Dict[str, int]]:
    """Insert diagnosis terms and synonyms; return (#terms, #synonyms, slug->id map)."""
    entries = json.loads(path.read_text(encoding="utf-8"))
    existing_terms = {t.id: t for t in db.execute(select(m.DiagnosisTerm)).scalars().all()}
    existing_synonyms_lc = {s.synonym.lower() for s in db.execute(select(m.DiagnosisSynonym)).scalars().all()}

    terms_new = 0
    syns_new = 0
    slug_to_id: Dict[str, int] = {}

    for obj in entries:
        term_id = int(obj["id"])  # raises if malformed
        canonical = (obj.get("canonical") or "").strip()
        if canonical and term_id not in existing_terms:
            db.add(m.DiagnosisTerm(id=term_id, name=canonical))
            existing_terms[term_id] = True  # sentinel
            terms_new += 1
        # Slug map (canonical)
        slug_to_id[slugify(canonical)] = term_id
        # Synonyms + abbreviations
        for key in ("synonyms", "abbreviations"):
            for syn in obj.get(key) or []:
                syn = syn.strip()
                if not syn:
                    continue
                lower = syn.lower()
                if lower in existing_synonyms_lc:
                    continue
                db.add(m.DiagnosisSynonym(diagnosis_term_id=term_id, synonym=syn))
                existing_synonyms_lc.add(lower)
                syns_new += 1
                # Also map synonym/abbreviation slug to this term id for header matching
                slug_to_id[slugify(syn)] = term_id
        # Misspellings: don't insert into DB, but do map for header matching if present
        for mis in obj.get("misspellings") or []:
            mis = mis.strip()
            if not mis:
                continue
            slug_to_id[slugify(mis)] = term_id

    return terms_new, syns_new, slug_to_id


def parse_prob_headers(fieldnames: List[str], slug_to_id: Dict[str, int]) -> List[Tuple[str, int]]:
    """Return list of (column_name, term_id). Raises if unmapped columns are found."""
    mapped: List[Tuple[str, int]] = []
    unknown: List[str] = []
    for col in fieldnames:
        if not col.startswith("prob_class_"):
            continue
        suffix = col[len("prob_class_"):]
        # normalize suffix
        tid = slug_to_id.get(suffix)
        if tid is None:
            tid = slug_to_id.get(slugify(suffix.replace("_", " ")))
        if tid is None:
            unknown.append(col)
            continue
        mapped.append((col, tid))
    if unknown:
        msg = "Unmapped probability columns (no matching term slug):\n  " + "\n  ".join(unknown)
        raise SystemExit(msg)
    return mapped


def ensure_roles(db: Session, role_names: List[str]) -> None:
    roles = db.execute(select(m.Role)).scalars().all()
    existing_lc = {r.name.lower(): r for r in roles}
    legacy = existing_lc.get("dermatology specialist")
    if legacy:
        db.delete(legacy)
        log("Removed legacy role 'Dermatology Specialist'")
    created = 0
    for name in role_names:
        if name.lower() not in existing_lc:
            db.add(m.Role(name=name))
            created += 1
    if created:
        log(f"Inserted {created} roles")


def load_cases(db: Session, csv_path: Path, prob_map: List[Tuple[str, int]]) -> Tuple[int, int, int]:
    # BOM-safe read
    reader = csv.DictReader(csv_path.read_text(encoding="utf-8-sig").splitlines())
    required = {"image_path", "gt"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise SystemExit(f"CSV missing required columns {required} in header: {reader.fieldnames}")

    cases_new = images_new = ai_rows = 0
    case_id_seq = 0
    for idx, row in enumerate(reader, start=1):
        case_id_seq += 1
        case_id = case_id_seq
        image_path = (row.get("image_path") or "").strip()
        gt_val = row.get("gt")
        gt = int(gt_val) if gt_val not in (None, "") else None

        # Build full probability vector
        probs: Dict[int, float] = {}
        for col, term_id in prob_map:
            raw = row.get(col, "")
            if raw == "":
                continue
            try:
                val = float(raw)
                if math.isfinite(val):
                    probs[term_id] = val
            except ValueError:
                continue

        # Insert case + image
        if db.get(m.Case, case_id):
            continue  # shouldn't happen with seq ids
        db.add(m.Case(id=case_id, ground_truth_diagnosis_id=gt, ai_predictions_json=probs))
        db.add(m.Image(case_id=case_id, image_url=image_path))
        cases_new += 1
        images_new += 1

        # Top-3 AI outputs
        top3 = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
        for rank, (tid, score) in enumerate(top3, start=1):
            db.add(m.AIOutput(case_id=case_id, rank=rank, prediction_id=tid, confidence_score=score))
            ai_rows += 1

    return cases_new, images_new, ai_rows


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Import SNU84 CSV and terms JSON")
    p.add_argument("--terms", type=Path, required=True, help="Path to new derm_dictionary.json")
    p.add_argument("--cases", type=Path, required=True, help="Path to SNU84 CSV file")
    return p


def main():
    args = build_arg_parser().parse_args()
    if not args.terms.exists():
        raise SystemExit(f"Terms file not found: {args.terms}")
    if not args.cases.exists():
        raise SystemExit(f"Cases file not found: {args.cases}")

    db: Session = SessionLocal()
    try:
        ensure_roles(db, ["GP", "Nurse", "Other"])
        terms_new, syns_new, slug_to_id = load_terms_from_json(db, args.terms)
        # Parse headers to map prob columns -> term IDs
        header = csv.DictReader(args.cases.read_text(encoding="utf-8-sig").splitlines()).fieldnames or []
        prob_map = parse_prob_headers(header, slug_to_id)
        cases_new, images_new, ai_rows = load_cases(db, args.cases, prob_map)
        db.commit()
        log("Import complete:")
        log(f"  Terms inserted: {terms_new}")
        log(f"  Synonyms inserted: {syns_new}")
        log(f"  Cases inserted: {cases_new}")
        log(f"  Images inserted: {images_new}")
        log(f"  AIOutput rows inserted: {ai_rows}")
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        db.rollback()
        log(f"Error during import: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
