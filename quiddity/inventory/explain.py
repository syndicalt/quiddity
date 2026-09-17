"""Turn a selected / catalog item into player-facing explanation."""

from __future__ import annotations

from quiddity.knowledge.store import find_item
from quiddity.models import Item


def explain_item(item: Item) -> str:
    catalog = find_item(item.wcid or item.id) or find_item(item.name)
    lines: list[str] = []
    title = item.name
    if item.qty > 1:
        title += f"  (stack {item.qty})"
    lines.append(title)
    kind = item.weenie_type
    if catalog and catalog.weenie_type != "unknown":
        kind = catalog.weenie_type
    meta = [kind]
    if item.material:
        meta.append(item.material)
    if item.workmanship is not None:
        meta.append(f"workmanship {item.workmanship}")
    if item.value:
        meta.append(f"{item.value:,} pyreal")
    if item.burden:
        meta.append(f"{item.burden} burden")
    lines.append(" | ".join(meta))

    if item.equipped_slot:
        lines.append(f"Currently equipped: {item.equipped_slot}")

    if item.armor_level is not None:
        cov = ", ".join(item.coverage) if item.coverage else "unknown coverage"
        lines.append(f"Armor level {item.armor_level} covering {cov}.")
        if item.protections:
            prot = ", ".join(f"{k} {v:g}" for k, v in item.protections.items())
            lines.append(f"Protections: {prot}")
        if item.set_name:
            lines.append(f"Item set: {item.set_name} (set bonuses apply when enough pieces are worn).")

    if item.damage:
        bits = [f"Damage {item.damage}"]
        if item.damage_type:
            bits.append(item.damage_type)
        if item.skill:
            bits.append(f"skill {item.skill}")
        lines.append(" ".join(bits) + ".")
        extras = []
        if item.slayer:
            extras.append(f"{item.slayer} slayer")
        if item.imbue:
            extras.append(item.imbue)
        if item.tinkers:
            extras.append(f"{item.tinkers}/{item.max_tinkers} tinkers")
        if extras:
            lines.append("Mods: " + ", ".join(extras) + ".")

    if item.wield_req:
        lines.append(f"Wield requirement: {item.wield_req}")

    spells = item.spells or (catalog.spells if catalog else [])
    if spells:
        lines.append("Spells: " + ", ".join(spells))

    if catalog and catalog.notes:
        lines.append(catalog.notes)
    elif item.notes:
        lines.append(item.notes)

    if catalog and catalog.dropped_by:
        lines.append("Commonly from: " + ", ".join(catalog.dropped_by[:6]))
    if catalog and catalog.used_in:
        lines.append("Used in: " + ", ".join(catalog.used_in[:6]))

    if item.properties:
        interesting = {
            k: v
            for k, v in item.properties.items()
            if k.lower() not in {"name", "id"} and v not in (None, "", 0)
        }
        if interesting:
            dump = ", ".join(f"{k}={v}" for k, v in list(interesting.items())[:12])
            lines.append("Raw: " + dump)

    return "\n".join(lines)
