"""Buff cycle families."""

from __future__ import annotations

from quiddity.models import WorldState

FAMILIES = {
    "life": [
        "Healing Mastery Self",
        "Regeneration Self",
        "Rejuvenation Self",
        "Mana Renewal Self",
        "Armor Self",
    ],
    "creature": [
        "Strength Self",
        "Endurance Self",
        "Coordination Self",
        "Quickness Self",
        "Focus Self",
        "Willpower Self",
        "Invulnerability Self",
        "Impregnability Self",
        "Magic Resistance Self",
    ],
    "item": [
        "Blood Drinker",
        "Heart Seeker",
        "Defender",
        "Swift Killer",
        "Spirit Drinker",
        "Impenetrability",
        "Blade Bane",
        "Piercing Bane",
        "Bludgeon Bane",
        "Flame Bane",
        "Frost Bane",
        "Acid Bane",
        "Lightning Bane",
    ],
    "void": ["Clouded Soul", "Noxious Swarm"],
}


def missing_buffs(state: WorldState, family: str) -> list[str]:
    have = {b.name.lower() for b in state.character.buffs}
    wanted = FAMILIES.get(family.lower(), FAMILIES["life"])
    skip = {"imperil self"}
    return [n for n in wanted if n.lower() not in have and n.lower() not in skip]


def buff_commands(state: WorldState, family: str = "life") -> list[str]:
    fam = family.lower()
    cmds = ["/vt opt set enablebuffing true"]
    missing = missing_buffs(state, fam)
    if not missing:
        return cmds + [f"/say {fam} buffs already present"]
    cmds.append("/vt opt set rebuffidle true")
    for name in missing[:4]:
        cmds.append(f"/ub cast {name}")
    return cmds
