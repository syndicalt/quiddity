# Quiddity

An **agent-driven companion** for Asheron's Call that covers the same *jobs* as Virindi Tank and Utility Belt — reusable routines, routes, buff cycles, combat priorities, healing — and adds something those plugins never had: a context-aware agent that can **explain** a selected item, **identify where you are**, recommend **armor/weapons**, and find **craft recipes from what you actually have**.

Quiddity is not a Decal plugin and does not replace VTank/UB. It is a **brain** that sits beside the existing AC plugin stack:

```
  Asheron's Call client
        |
     Decal -- Virindi Tank -- Utility Belt (Lua / expressions / TCP)
        |
  World Snapshot (JSON)  <-- adapter (UB commands, VTank chat, file drop, or mock)
        |
     Quiddity agent runtime
        |
     routines / explainers / planners
```

Official retail Asheron's Call is gone. People play on ACE and other private servers. **Many servers restrict or ban unattended macros.** Quiddity defaults to *advise and confirm*. Unattended execution is an explicit opt-in that you must keep compatible with *your* server's rules.

## What works in this prototype

| Capability | Status |
|---|---|
| Routine DSL (YAML): buffs, combat, heal, nav, loot, chat, wait, compose | Working |
| Priority combat / heal policies | Working |
| Item explainer (weenie-style properties + player language) | Working |
| Location explainer (coords, landblock, nearby POIs) | Working |
| Armor / weapon optimizer against inventory + target profile | Working |
| Recipe search from current inventory (multi-step graphs) | Working |
| Mock world snapshot (so you can develop without the client) | Working |
| File-drop adapter (`world.json` written by a UB Lua script or `/vt propertydump` parser) | Working |
| VTank command emitter (`/vt`, `/ub`) | Working (prints / writes command queue) |
| Live Decal plugin that reads memory | Not in this repo — use VTank+UB as sensors |

## Quick start

```bash
cd quiddity
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m quiddity.cli demo
python3 -m quiddity.cli explain-item --id 35981
python3 -m quiddity.cli where
python3 -m quiddity.cli optimize --role mage
python3 -m quiddity.cli recipes
python3 -m quiddity.cli run data/sample_routines/hunt_loop.yaml
python3 -m quiddity.cli chat "what should I wear for Olthoi?"
```

## Mental model

**Routines** are deterministic programs (like a VTank meta, but readable YAML).
**Agents** sit *above* routines: they pick which routine to run, explain state, and fill in missing knowledge.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/INTEGRATION.md](docs/INTEGRATION.md).
