"""Load WorldState from mock, file, or environment."""

from __future__ import annotations

import json
import os
from pathlib import Path

from quiddity.models import WorldState

DEFAULT_MOCK = Path(__file__).resolve().parents[2] / "data" / "world.mock.json"


def load_world(path: str | Path | None = None) -> WorldState:
    raw_path = path or os.environ.get("QUIDDITY_WORLD") or DEFAULT_MOCK
    p = Path(raw_path)
    if not p.exists():
        raise FileNotFoundError(f"World snapshot not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    state = WorldState.model_validate(data)
    state.source = str(p)
    return state
