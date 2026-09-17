"""Actuators turn routine steps into VTank/UB commands or mock logs."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Actuator(Protocol):
    def emit(self, command: str) -> None: ...

    def log(self, message: str) -> None: ...


class PrintActuator:
    def __init__(self) -> None:
        self.history: list[str] = []

    def emit(self, command: str) -> None:
        line = command if command.startswith("/") else f"/say {command}"
        self.history.append(line)
        print(f"  -> {line}")

    def log(self, message: str) -> None:
        print(f"  - {message}")


class FileActuator:
    """Append commands for a UB alias / AHK pump to consume."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.history: list[str] = []

    def emit(self, command: str) -> None:
        line = command if command.startswith("/") else command
        self.history.append(line)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(f"  -> queued {line}")

    def log(self, message: str) -> None:
        print(f"  - {message}")
