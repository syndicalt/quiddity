"""Combat priority policy to VTank option commands."""

from __future__ import annotations

from quiddity.models import WorldState

PROFILES = {
    "default": ["/vt opt set enablecombat true", "/vt opt set monster 5"],
    "mage": ["/vt opt set enablecombat true", "/vt opt set monster 15", "/vt opt set ringrange 8"],
    "pull": ["/vt opt set enablecombat true", "/vt opt set monster 70"],
    "hold": ["/vt opt set enablecombat true", "/vt opt set enablenav false", "/vt opt set monster 5"],
    "off": ["/vt opt set enablecombat false"],
}


def combat_commands(state: WorldState, profile: str = "default") -> list[str]:
    key = profile.lower()
    cmds = list(PROFILES.get(key, PROFILES["default"]))
    if state.character.health.pct < 0.35:
        cmds.insert(0, "/vt opt set enablecombat false")
        cmds.append("/vt opt set enablebuffing true")
    return cmds
