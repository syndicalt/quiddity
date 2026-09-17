"""Find craft recipes whose ingredients exist in inventory (multi-step)."""

from __future__ import annotations

from dataclasses import dataclass, field

from quiddity.knowledge.store import recipes as all_recipes
from quiddity.models import Recipe, WorldState


@dataclass
class CraftPlan:
    recipe: Recipe
    missing: list[str] = field(default_factory=list)
    have: list[str] = field(default_factory=list)
    intermediates_needed: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.missing


def _inventory_names(state: WorldState) -> dict[str, int]:
    bag: dict[str, int] = {}
    for it in state.inventory:
        bag[it.name.lower()] = bag.get(it.name.lower(), 0) + it.qty
    return bag


def _ingredients(recipe: Recipe) -> set[str]:
    names: set[str] = set()
    for step in recipe.steps:
        names.add(step.tool.lower())
        names.add(step.target.lower())
    return names


def plan_recipes(state: WorldState, query: str | None = None) -> list[CraftPlan]:
    bag = _inventory_names(state)
    out: list[CraftPlan] = []
    for rec in all_recipes():
        if query and query.lower() not in rec.name.lower() and query.lower() not in rec.result.lower():
            if not any(query.lower() in s.tool.lower() or query.lower() in s.target.lower() for s in rec.steps):
                continue
        have, missing = [], []
        intermediates = [s.result for s in rec.steps[:-1]] if rec.steps else []
        for ing in sorted(_ingredients(rec)):
            if bag.get(ing, 0) > 0:
                have.append(ing)
            else:
                if any(ing == x.lower() for x in intermediates):
                    continue
                missing.append(ing)
        out.append(CraftPlan(recipe=rec, missing=missing, have=have, intermediates_needed=intermediates))
    out.sort(key=lambda p: (not p.complete, len(p.missing), p.recipe.name))
    return out


def format_plans(plans: list[CraftPlan], limit: int = 12) -> str:
    if not plans:
        return "No recipes matched."
    lines = []
    for p in plans[:limit]:
        flag = "READY" if p.complete else f"missing {len(p.missing)}"
        lines.append(f"{p.recipe.name} [{p.recipe.skill}] -> {p.recipe.result}  ({flag})")
        if p.recipe.effect:
            lines.append(f"    effect: {p.recipe.effect}")
        for step in p.recipe.steps:
            extra = f"  diff {step.difficulty}" if step.difficulty else ""
            lines.append(f"    {step.tool} + {step.target} = {step.result}{extra}")
        if p.missing:
            lines.append("    still need: " + ", ".join(p.missing))
    return "\n".join(lines)
