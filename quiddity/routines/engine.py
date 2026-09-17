"""YAML routine engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from quiddity.buffs.cycle import buff_commands
from quiddity.combat.policy import combat_commands
from quiddity.context.actuator import Actuator
from quiddity.healing.policy import heal_commands
from quiddity.models import WorldState


class RoutineError(RuntimeError):
    pass


def load_routine(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "steps" not in data:
        raise RoutineError(f"{p} must be a mapping with a 'steps' list")
    data.setdefault("name", p.stem)
    data["_path"] = str(p.resolve())
    return data


def _truthy(state: WorldState, pred: dict[str, Any]) -> bool:
    if "vitals.health_below" in pred and state.character.health.pct >= pred["vitals.health_below"]:
        return False
    if "vitals.stamina_below" in pred and state.character.stamina.pct >= pred["vitals.stamina_below"]:
        return False
    if "vitals.mana_below" in pred and state.character.mana.pct >= pred["vitals.mana_below"]:
        return False
    if "in_combat" in pred and bool(state.character.in_combat) != bool(pred["in_combat"]):
        return False
    if "has_item" in pred and not state.find_name(str(pred["has_item"])):
        return False
    if "missing_buff" in pred:
        names = {b.name.lower() for b in state.character.buffs}
        if str(pred["missing_buff"]).lower() in names:
            return False
    return True


def run_routine(routine: dict[str, Any], state: WorldState, actuator: Actuator, live: bool = False) -> WorldState:
    actuator.log(f"routine {routine.get('name')} from {routine.get('_path', '?')}")
    _run_steps(routine.get("steps") or [], state, actuator, live, Path(routine.get("_path", ".")).parent)
    return state


def _run_steps(steps: list[Any], state: WorldState, actuator: Actuator, live: bool, base: Path) -> None:
    import time

    for step in steps:
        if not isinstance(step, dict):
            actuator.log(f"skip non-mapping step: {step!r}")
            continue
        if "when" in step:
            if not _truthy(state, step["when"]):
                actuator.log(f"guard failed: {step['when']}")
                continue
            _run_steps(step.get("steps") or [], state, actuator, live, base)
            continue
        if "log" in step:
            actuator.log(str(step["log"]))
        if "wait" in step:
            seconds = float(step["wait"])
            actuator.log(f"wait {seconds}s")
            if live:
                time.sleep(seconds)
        if "vt" in step:
            cmd = str(step["vt"]).strip()
            actuator.emit(cmd if cmd.startswith("/vt") else f"/vt {cmd}")
        if "ub" in step:
            cmd = str(step["ub"]).strip()
            actuator.emit(cmd if cmd.startswith("/ub") else f"/ub {cmd}")
        if "chat" in step:
            actuator.emit(str(step["chat"]))
        if "set" in step:
            flags = step["set"] or {}
            if "combat" in flags:
                state.combat_enabled = bool(flags["combat"])
            if "nav" in flags:
                state.nav_enabled = bool(flags["nav"])
            if "buffing" in flags:
                state.buffing_enabled = bool(flags["buffing"])
            actuator.log(f"flags {flags}")
        if "buff" in step:
            for cmd in buff_commands(state, str(step["buff"])):
                actuator.emit(cmd)
        if "heal" in step:
            for cmd in heal_commands(state, str(step["heal"])):
                actuator.emit(cmd)
        if "combat" in step:
            for cmd in combat_commands(state, str(step["combat"])):
                actuator.emit(cmd)
        if "nav" in step:
            name = str(step["nav"])
            actuator.emit(f"/vt nav load {name}")
            actuator.emit("/vt opt set enablenav true")
            state.nav_enabled = True
        if "compose" in step:
            other = (base / str(step["compose"])).resolve()
            nested = load_routine(other)
            run_routine(nested, state, actuator, live=live)
