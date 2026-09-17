"""Load curated AC catalogs shipped with Quiddity."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from quiddity.models import CatalogItem, Place, Recipe

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def _load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def items() -> list[CatalogItem]:
    raw = _load_json(DATA_ROOT / "items" / "catalog.json")
    return [CatalogItem.model_validate(x) for x in raw]


@lru_cache(maxsize=1)
def recipes() -> list[Recipe]:
    raw = _load_json(DATA_ROOT / "recipes" / "catalog.json")
    return [Recipe.model_validate(x) for x in raw]


@lru_cache(maxsize=1)
def places() -> list[Place]:
    raw = _load_json(DATA_ROOT / "locations" / "catalog.json")
    return [Place.model_validate(x) for x in raw]


def find_item(name_or_id: str | int) -> Optional[CatalogItem]:
    key = str(name_or_id).lower()
    for it in items():
        if str(it.id) == key or (it.wcid and str(it.wcid) == key):
            return it
        if it.name.lower() == key:
            return it
    for it in items():
        if key in it.name.lower():
            return it
    return None


def find_place(name: str) -> Optional[Place]:
    key = name.lower()
    for p in places():
        if p.name.lower() == key or key in [a.lower() for a in p.aliases]:
            return p
    for p in places():
        if key in p.name.lower():
            return p
    return None
