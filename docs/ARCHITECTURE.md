# Architecture

## Layers

1. CLI / Chat (`python3 -m quiddity.cli chat | explain-item | run`)
2. Agent planner — tools: explain_item, locate, optimize_gear, find_recipes, run_routine
3. Domain services — ItemExplainer, LocationGuide, GearOptimizer, RecipeGraph, CombatPolicy, HealPolicy, BuffCycle
4. Routine engine (YAML steps to Actuator)
5. Context adapters — mock, file snapshot, command queue
6. Knowledge store — JSON weenie-ish catalogs

## Why not a Decal plugin first?

Virindi Tank and Utility Belt already own targeting, buff timers, nav graphs, loot profiles, meta FSMs, and a local TCP server on 127.0.0.1:42163.

Quiddity treats VTank/UB as actuators and sensors. The new value is a readable routine language, an agent that can talk about the same snapshot the macro uses, and knowledge VTank never had in-process (recipe graphs, armor set math, item explainers).

## World snapshot

Every adapter produces the same WorldState model: vitals, skills, buffs, position, equipped slots, inventory, selected object, nearby objects.

Until a live dumper exists, `data/world.mock.json` is the development fixture.

## Routine DSL

A routine is a named document with optional `when` guards and `steps`. Any step can emit a `/vt` or `/ub` command. You can wrap an existing `.nav` / `.met` instead of rewriting it.

## Agents

The planner is tool-using. Tools are pure functions over WorldState + knowledge. When an LLM is attached later, it should only call tools, choose among existing routines, or draft YAML for the user to save. It should not invent `/vt` flags or item IDs.
