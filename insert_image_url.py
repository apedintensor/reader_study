#!/usr/bin/env python
"""Assign (replace) image URLs for every case.

Behavior:
* Reads mock-skin-images.txt.
* For each Case: deletes ALL existing Image rows then inserts exactly 3 images.
* If fewer than 3 unique URLs are in the file, will reuse randomly.

Usage (local PowerShell):
    $env:DATABASE_URL = 'postgresql://...'
    python insert_image_url.py

Fly one-off:
    fly ssh console -C "python insert_image_url.py"
"""
import asyncio
import logging
import os
import random
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.models import Case, Image

MOCK_IMAGE_FILE = "mock-skin-images.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("insert_image_url")


def load_mock_image_urls() -> List[str]:
    if not os.path.exists(MOCK_IMAGE_FILE):
        logger.error(f"File {MOCK_IMAGE_FILE} not found. Aborting.")
        return []
    try:
        with open(MOCK_IMAGE_FILE, "r", encoding="utf-8") as f:
            urls = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        if not urls:
            logger.error(f"No URLs found in {MOCK_IMAGE_FILE}. Aborting.")
        else:
            logger.info(f"Loaded {len(urls)} image URLs from {MOCK_IMAGE_FILE}")
        return urls
    except Exception as e:
        logger.error(f"Error reading {MOCK_IMAGE_FILE}: {e}")
        return []


async def ensure_images_for_case(db: AsyncSession, case: Case, urls: List[str]):
    # Fetch existing images
    existing_stmt = select(Image).where(Image.case_id == case.id)
    res = await db.execute(existing_stmt)
    existing = list(res.scalars())

    if existing:
        del_stmt = delete(Image).where(Image.case_id == case.id)
        await db.execute(del_stmt)
        existing = []
    needed = 3

    # Choose needed number ensuring no per-case duplicates
    # We allow reuse across different cases.
    available_urls = [u for u in urls if u not in {img.image_url for img in existing}]
    if not available_urls:
        # Fallback: allow duplicates if we've exhausted unique URLs
        available_urls = urls

    # If fewer unique URLs than needed, sample without replacement up to available, then fill by random choice
    if len(available_urls) >= needed:
        chosen = random.sample(available_urls, needed)
    else:
        chosen = available_urls.copy()
        while len(chosen) < needed and urls:
            chosen.append(random.choice(urls))

    for url in chosen:
        db.add(Image(case_id=case.id, image_url=url))

    return len(chosen)


async def process_cases(urls: List[str]):
    if not urls:
        logger.error("No URLs loaded; aborting.")
        return

    added_total = 0
    processed = 0
    async with AsyncSessionLocal() as db:
        stmt = select(Case)
        res = await db.execute(stmt)
        cases = list(res.scalars())
        logger.info(f"Found {len(cases)} cases")

        for case in cases:
            added = await ensure_images_for_case(db, case, urls)
            if added:
                added_total += added
            processed += 1
            if processed % 50 == 0:
                await db.commit()
                logger.info(f"Processed {processed} cases so far (images added: {added_total})")
        await db.commit()

    logger.info(f"Completed. Images added: {added_total}")


async def main():
    urls = load_mock_image_urls()
    if len(urls) < 3:
        logger.warning("Fewer than 3 URLs available; some cases may reuse image URLs.")
    await process_cases(urls)


if __name__ == "__main__":
    asyncio.run(main())
