"""Healing policy — kits, life magic, fellow heals."""

from __future__ import annotations

from quiddity.models import WorldState


def heal_commands(state: WorldState, target: str = "self") -> list[str]:
    cmds: list[str] = []
    hp = state.character.health.pct
    stam = state.character.stamina.pct
    mana = state.character.mana.pct
    inv_names = {i.name.lower() for i in state.inventory}

    if target == "self":
        if hp < 0.45:
            life = state.character.skill("Life Magic")
            if life and life.buffed >= 50:
                cmds.append("/ub cast Heal Self")
            elif "health kit" in inv_names or any("kit" in n and "health" in n for n in inv_names):
                cmds.append("/ub use Health Kit")
            else:
                cmds.append("/say I need a heal and have no kit / Heal Self.")
        if stam < 0.35:
            cmds.append("/ub use Stamina Kit" if any("stamina" in n and "kit" in n for n in inv_names) else "/say low stamina")
        if mana < 0.25:
            if any("mana stone" in n or "scarab" in n for n in inv_names):
                cmds.append("/ub use Mana Stone")
            else:
                cmds.append("/say low mana")
    elif target == "fellow":
        cmds.append("/vt opt set enablefellowheals true")
        if "healer's heart" in inv_names:
            cmds.append("/ub use Healer's Heart")
    if not cmds:
        cmds.append("/say vitals are fine")
    return cmds
