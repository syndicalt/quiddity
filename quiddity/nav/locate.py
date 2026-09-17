"""Identify where the character is standing."""

from __future__ import annotations

import math

from quiddity.knowledge.store import places
from quiddity.models import Place, Position, WorldState


def _dist(a_ns: float, a_ew: float, b_ns: float, b_ew: float) -> float:
    return math.hypot(a_ns - b_ns, a_ew - b_ew)


def nearest_places(pos: Position, n: int = 5) -> list[tuple[Place, float]]:
    ranked = [(p, _dist(pos.ns, pos.ew, p.ns, p.ew)) for p in places()]
    ranked.sort(key=lambda t: t[1])
    return ranked[:n]


def describe_location(state: WorldState) -> str:
    pos = state.character.position
    lines = [f"{state.character.name} is at {pos.coord_string()}"]
    if pos.landblock:
        lines.append(f"Landblock {pos.landblock}")
    if pos.indoors and pos.dungeon:
        lines.append(f"Inside dungeon: {pos.dungeon}")
    elif pos.indoors:
        lines.append("Indoors (building or dungeon).")
    else:
        lines.append("Outdoors on the landscape.")

    nearby = nearest_places(pos, 5)
    if nearby:
        closest, d = nearby[0]
        if d < 0.4:
            lines.append(f"This is {closest.name} ({closest.kind}).")
            if closest.notes:
                lines.append(closest.notes)
            if closest.level_range:
                lines.append(f"Typical content level: {closest.level_range}")
            if closest.dangers:
                lines.append("Watch for: " + ", ".join(closest.dangers))
            if closest.vendors:
                lines.append("Vendors / NPCs: " + ", ".join(closest.vendors[:8]))
        else:
            lines.append("Nearest landmarks:")
            for p, dist in nearby:
                lines.append(f"  * {p.name} ({p.kind}) — {dist:.1f} map units")

    if state.nearby:
        lines.append("Objects the client currently sees:")
        for obj in state.nearby[:8]:
            lines.append(f"  * {obj.name} [{obj.kind}] at {obj.distance:.1f}")
    return "\n".join(lines)
