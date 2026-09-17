"""Pick armor / weapons from inventory for a role and threat profile."""

from __future__ import annotations

from dataclasses import dataclass

from quiddity.models import Item, WorldState

ROLES = {
    "mage": {
        "prefer_skills": ["War Magic", "Void Magic", "Life Magic", "Mana Conversion"],
        "weapon_kind": "caster",
        "notes": "Prioritize cantrips to Focus/Self, mana conversion, and a wand/orb with slayer or elemental damage.",
    },
    "melee": {
        "prefer_skills": ["Heavy Weapons", "Finesse Weapons", "Light Weapons", "Two Handed Combat", "Melee Defense"],
        "weapon_kind": "melee",
        "notes": "Prioritize AL, melee defense cantrips, and a weapon matching the trained weapon skill.",
    },
    "missile": {
        "prefer_skills": ["Missile Weapons", "Missile Defense"],
        "weapon_kind": "missile",
        "notes": "Bow/Xbow/atlatl with high damage + slayer; keep burden low.",
    },
    "hybrid": {
        "prefer_skills": ["War Magic", "Heavy Weapons", "Life Magic"],
        "weapon_kind": "either",
        "notes": "Keep both a caster and a melee weapon ready.",
    },
}

THREATS = {
    "olthoi": {"acid": 1.4, "pierce": 1.2, "slash": 0.8},
    "undead": {"bludgeon": 1.2, "fire": 1.1, "slash": 1.0},
    "shadow": {"slash": 1.1, "nether": 1.2, "fire": 0.9},
    "general": {"slash": 1.0, "pierce": 1.0, "bludgeon": 1.0, "fire": 1.0, "cold": 1.0, "acid": 1.0, "electric": 1.0},
}

ARMOR_SLOTS = [
    "head", "chest", "abdomen", "upper_arms", "lower_arms",
    "hands", "upper_legs", "lower_legs", "feet", "shield",
]


@dataclass
class Recommendation:
    title: str
    items: list[Item]
    rationale: list[str]


def _score_armor(item: Item, threat: str) -> float:
    if item.armor_level is None:
        return -1.0
    score = float(item.armor_level)
    weights = THREATS.get(threat, THREATS["general"])
    if isinstance(weights, dict):
        for dmg, w in weights.items():
            if dmg in item.protections:
                score += 40 * item.protections[dmg] * w
    score += 8 * len(item.spells)
    if item.set_name:
        score += 25
    score += item.workmanship or 0
    return score


def _score_weapon(item: Item, role: str) -> float:
    kind = ROLES[role]["weapon_kind"]
    skill = (item.skill or "").lower()
    is_caster = item.weenie_type in {"caster", "wand", "orb"} or skill in {"war magic", "void magic", "life magic"}
    is_melee = item.weenie_type in {"melee", "melee_weapon"} or item.skill in {
        "Heavy Weapons", "Finesse Weapons", "Light Weapons", "Two Handed Combat", "Unarmed Combat"
    }
    is_missile = item.weenie_type in {"missile", "missile_weapon"} or item.skill == "Missile Weapons"
    if kind == "caster" and not is_caster:
        return -1.0
    if kind == "melee" and not is_melee:
        return -1.0
    if kind == "missile" and not is_missile:
        return -1.0
    score = 10.0
    if item.damage:
        try:
            parts = item.damage.replace("\u2013", "-").split("-")
            score += float(parts[-1].strip())
        except ValueError:
            pass
    if item.slayer:
        score += 20
    if item.imbue:
        score += 12
    score += 6 * len(item.spells)
    score += item.tinkers * 2
    return score


def optimize(state: WorldState, role: str = "melee", threat: str = "general") -> list[Recommendation]:
    role = role.lower()
    if role not in ROLES:
        role = "melee"
    threat = threat.lower()
    inv = state.inventory
    recs: list[Recommendation] = []

    armor_pool = [i for i in inv if i.armor_level is not None]
    chosen_armor: list[Item] = []
    rationale = []
    for slot in ARMOR_SLOTS:
        candidates = [
            i for i in armor_pool
            if slot in [c.replace(" ", "_").lower() for c in i.coverage]
            or (i.equipped_slot or "").replace(" ", "_").lower() == slot
        ]
        if not candidates:
            continue
        best = max(candidates, key=lambda i: _score_armor(i, threat))
        if _score_armor(best, threat) < 0:
            continue
        chosen_armor.append(best)
        rationale.append(
            f"{slot}: {best.name} (AL {best.armor_level}"
            + (f", set {best.set_name}" if best.set_name else "")
            + ")"
        )
    if chosen_armor:
        recs.append(Recommendation(f"Armor vs {threat} ({role})", chosen_armor, rationale))

    weapons = [
        i for i in inv
        if i.damage or i.weenie_type in {"caster", "melee", "missile", "wand", "orb", "melee_weapon", "missile_weapon"}
    ]
    ranked = [w for w in sorted(weapons, key=lambda i: _score_weapon(i, role), reverse=True) if _score_weapon(w, role) >= 0][:3]
    if ranked:
        recs.append(Recommendation(
            f"Weapons for {role}",
            ranked,
            [ROLES[role]["notes"]] + [
                f"{w.name}" + (f" — {w.damage} {w.damage_type or ''}" if w.damage else "") for w in ranked
            ],
        ))

    sets: dict[str, list[Item]] = {}
    for i in inv:
        if i.set_name:
            sets.setdefault(i.set_name, []).append(i)
    for name, pieces in sets.items():
        if len(pieces) >= 2:
            recs.append(Recommendation(
                f"Set collection: {name}",
                pieces,
                [f"You have {len(pieces)} pieces. Wear more of this set before mixing random loot AL."],
            ))
    return recs


def format_recommendations(recs: list[Recommendation]) -> str:
    if not recs:
        return "Inventory does not contain enough armor/weapons to recommend a loadout."
    blocks = []
    for rec in recs:
        lines = [rec.title]
        for r in rec.rationale:
            lines.append(f"  * {r}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
