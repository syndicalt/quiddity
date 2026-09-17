"""Quiddity command line (stdlib argparse)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from quiddity import __version__
from quiddity.agent.planner import handle
from quiddity.context.actuator import FileActuator, PrintActuator
from quiddity.context.world import load_world
from quiddity.inventory.explain import explain_item
from quiddity.inventory.optimize import format_recommendations, optimize
from quiddity.inventory.recipes import format_plans, plan_recipes
from quiddity.nav.locate import describe_location
from quiddity.routines.engine import load_routine, run_routine

console = Console()


def _world(path: Optional[str]):
    return load_world(path)


def cmd_demo(args: argparse.Namespace) -> int:
    state = _world(args.world)
    console.print(Panel(
        f"{state.character.name}  lvl {state.character.level}  {state.character.position.coord_string()}",
        title="character",
    ))
    if state.selected:
        console.print(Panel(explain_item(state.selected), title="selected item"))
    console.print(Panel(describe_location(state), title="location"))
    console.print(Panel(
        format_recommendations(optimize(state, role="mage", threat="olthoi")),
        title="gear (mage vs olthoi)",
    ))
    console.print(Panel(format_plans(plan_recipes(state), limit=8), title="craft from bags"))
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    state = _world(args.world)
    item = state.selected
    if args.id is not None:
        item = next((i for i in state.inventory if i.id == args.id), item)
    if args.name:
        found = state.find_name(args.name)
        item = found[0] if found else item
    if item is None:
        console.print("No item selected.")
        return 1
    console.print(explain_item(item))
    return 0


def cmd_where(args: argparse.Namespace) -> int:
    console.print(describe_location(_world(args.world)))
    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    state = _world(args.world)
    console.print(format_recommendations(optimize(state, role=args.role, threat=args.threat)))
    return 0


def cmd_recipes(args: argparse.Namespace) -> int:
    state = _world(args.world)
    console.print(format_plans(plan_recipes(state, query=args.query)))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    state = _world(args.world)
    actuator = FileActuator(args.emit) if args.emit else PrintActuator()
    run_routine(load_routine(args.routine), state, actuator, live=args.live)
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    state = _world(args.world)
    utterance = " ".join(args.text or [])
    if not utterance:
        utterance = input("you> ")
    reply = handle(utterance, state)
    console.print(Panel(reply.text, title=f"quiddity / {reply.tool}"))
    return 0


def cmd_version(_: argparse.Namespace) -> int:
    console.print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--world", default=None, help="Path to world.json snapshot")
    p = argparse.ArgumentParser(prog="quiddity", description="Agent companion for Asheron's Call.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version", parents=[parent], help="Print version").set_defaults(func=cmd_version)
    sub.add_parser("demo", parents=[parent], help="Run every tool against the snapshot").set_defaults(func=cmd_demo)
    e = sub.add_parser("explain-item", parents=[parent], help="Explain selected / named item")
    e.add_argument("--id", type=int, default=None)
    e.add_argument("--name", default=None)
    e.set_defaults(func=cmd_explain)
    sub.add_parser("where", parents=[parent], help="Explain current location").set_defaults(func=cmd_where)
    o = sub.add_parser("optimize", parents=[parent], help="Recommend armor and weapons")
    o.add_argument("--role", default="melee")
    o.add_argument("--threat", default="general")
    o.set_defaults(func=cmd_optimize)
    r = sub.add_parser("recipes", parents=[parent], help="Recipes you can craft from inventory")
    r.add_argument("--query", default=None)
    r.set_defaults(func=cmd_recipes)
    runp = sub.add_parser("run", parents=[parent], help="Execute a YAML routine")
    runp.add_argument("routine")
    runp.add_argument("--emit", default=None)
    runp.add_argument("--live", action="store_true")
    runp.set_defaults(func=cmd_run)
    c = sub.add_parser("chat", parents=[parent], help="Ask the agent about the snapshot")
    c.add_argument("text", nargs="*")
    c.set_defaults(func=cmd_chat)
    return p


def app(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "world"):
        args.world = None
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    app()
