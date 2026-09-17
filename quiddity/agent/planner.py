"""Deterministic tool-using planner."""

from __future__ import annotations

from dataclasses import dataclass

from quiddity.inventory.explain import explain_item
from quiddity.inventory.optimize import format_recommendations, optimize
from quiddity.inventory.recipes import format_plans, plan_recipes
from quiddity.models import WorldState
from quiddity.nav.locate import describe_location


@dataclass
class AgentReply:
    text: str
    tool: str


def _wants(text: str, *needles: str) -> bool:
    t = text.lower()
    return any(n in t for n in needles)


def handle(utterance: str, state: WorldState) -> AgentReply:
    q = utterance.strip()
    if not q:
        return AgentReply("Say something: item, where, armor, recipes, buffs.", "none")

    if _wants(q, "where", "location", "am i", "dungeon", "town"):
        return AgentReply(describe_location(state), "locate")

    if _wants(q, "recipe", "craft", "alchemy", "cook", "fletch", "tinker"):
        query = None
        for token in ("for ", "recipe ", "craft "):
            if token in q.lower():
                query = q.lower().split(token, 1)[-1].strip(" ?.")
                break
        plans = plan_recipes(state, query=query if query else None)
        return AgentReply(format_plans(plans), "recipes")

    if _wants(q, "armor", "weapon", "wear", "wield", "gear", "equip", "optimize", "olthoi", "loadout"):
        role = "mage" if "mage" in q.lower() or "war" in q.lower() else "melee"
        if "bow" in q.lower() or "missile" in q.lower() or "arrow" in q.lower():
            role = "missile"
        if "hybrid" in q.lower():
            role = "hybrid"
        threat = "general"
        for name in ("olthoi", "undead", "shadow", "gromnie"):
            if name in q.lower():
                threat = name
        recs = optimize(state, role=role, threat=threat)
        return AgentReply(format_recommendations(recs), "optimize")

    if _wants(q, "item", "this", "selected", "explain", "what is", "wand", "sword", "loot"):
        item = state.selected
        if item is None:
            return AgentReply("Nothing is selected in the snapshot. Select an item in-game and refresh world.json.", "explain")
        return AgentReply(explain_item(item), "explain")

    if _wants(q, "buff", "rebuff"):
        names = [b.name for b in state.character.buffs]
        if names:
            return AgentReply("Active buffs:\n  * " + "\n  * ".join(names), "buffs")
        return AgentReply("No buffs in the snapshot. Run a buff_cycle routine.", "buffs")

    if _wants(q, "heal", "health", "vitals"):
        c = state.character
        return AgentReply(
            f"Health {c.health.current}/{c.health.max} ({c.health.pct:.0%})  "
            f"Stamina {c.stamina.current}/{c.stamina.max} ({c.stamina.pct:.0%})  "
            f"Mana {c.mana.current}/{c.mana.max} ({c.mana.pct:.0%})",
            "vitals",
        )

    if state.selected and _wants(q, state.selected.name.lower().split()[0]):
        return AgentReply(explain_item(state.selected), "explain")

    return AgentReply(
        "I can explain the selected item, say where you are, pick armor/weapons, "
        "or list recipes you can craft from inventory.",
        "help",
    )
