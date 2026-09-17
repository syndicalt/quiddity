"""Shared world / knowledge models."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Position(BaseModel):
    ns: float = 0.0
    ew: float = 0.0
    z: float = 0.0
    landblock: Optional[str] = None
    heading: float = 0.0
    indoors: bool = False
    dungeon: Optional[str] = None

    def coord_string(self) -> str:
        ns_h = "N" if self.ns >= 0 else "S"
        ew_h = "E" if self.ew >= 0 else "W"
        return f"{abs(self.ns):.1f}{ns_h}, {abs(self.ew):.1f}{ew_h}"


class Vital(BaseModel):
    current: int = 0
    max: int = 1

    @property
    def pct(self) -> float:
        if self.max <= 0:
            return 0.0
        return self.current / self.max


class Skill(BaseModel):
    name: str
    trained: str = "untrained"
    base: int = 0
    buffed: int = 0


class Buff(BaseModel):
    name: str
    family: str = "unknown"
    seconds_left: float = 0.0
    from_item: bool = False


class Item(BaseModel):
    id: int
    wcid: Optional[int] = None
    name: str
    weenie_type: str = "unknown"
    qty: int = 1
    equipped_slot: Optional[str] = None
    value: int = 0
    burden: int = 0
    workmanship: Optional[int] = None
    material: Optional[str] = None
    armor_level: Optional[int] = None
    coverage: list[str] = Field(default_factory=list)
    protections: dict[str, float] = Field(default_factory=dict)
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    skill: Optional[str] = None
    wield_req: Optional[str] = None
    spells: list[str] = Field(default_factory=list)
    set_name: Optional[str] = None
    slayer: Optional[str] = None
    imbue: Optional[str] = None
    tinkers: int = 0
    max_tinkers: int = 10
    properties: dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

    def stack_label(self) -> str:
        return self.name if self.qty <= 1 else f"{self.name} x{self.qty}"


class Character(BaseModel):
    name: str = "Unknown"
    level: int = 1
    heritage: Optional[str] = None
    template: Optional[str] = None
    health: Vital = Field(default_factory=Vital)
    stamina: Vital = Field(default_factory=Vital)
    mana: Vital = Field(default_factory=Vital)
    skills: list[Skill] = Field(default_factory=list)
    buffs: list[Buff] = Field(default_factory=list)
    position: Position = Field(default_factory=Position)
    burden_pct: float = 0.0
    in_combat: bool = False
    fellowship: list[str] = Field(default_factory=list)

    def skill(self, name: str) -> Optional[Skill]:
        key = name.lower()
        for s in self.skills:
            if s.name.lower() == key:
                return s
        return None


class Nearby(BaseModel):
    id: int
    name: str
    kind: str = "unknown"
    distance: float = 0.0


class WorldState(BaseModel):
    character: Character = Field(default_factory=Character)
    inventory: list[Item] = Field(default_factory=list)
    selected: Optional[Item] = None
    nearby: list[Nearby] = Field(default_factory=list)
    vendor_open: bool = False
    combat_enabled: bool = False
    nav_enabled: bool = False
    buffing_enabled: bool = False
    source: str = "mock"

    def equipped(self) -> list[Item]:
        return [i for i in self.inventory if i.equipped_slot]

    def packs(self) -> list[Item]:
        return [i for i in self.inventory if not i.equipped_slot]

    def find_name(self, needle: str) -> list[Item]:
        n = needle.lower()
        return [i for i in self.inventory if n in i.name.lower()]

    def count_name(self, name: str) -> int:
        n = name.lower()
        return sum(i.qty for i in self.inventory if i.name.lower() == n)


class CatalogItem(Item):
    wiki: Optional[str] = None
    dropped_by: list[str] = Field(default_factory=list)
    used_in: list[str] = Field(default_factory=list)


class RecipeStep(BaseModel):
    tool: str
    target: str
    result: str
    skill: str = "Alchemy"
    difficulty: Optional[int] = None


class Recipe(BaseModel):
    id: str
    name: str
    skill: str
    result: str
    result_qty: int = 1
    steps: list[RecipeStep] = Field(default_factory=list)
    effect: Optional[str] = None
    notes: Optional[str] = None


class Place(BaseModel):
    name: str
    kind: str = "town"
    ns: float
    ew: float
    landblock: Optional[str] = None
    level_range: Optional[str] = None
    notes: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    dangers: list[str] = Field(default_factory=list)
    vendors: list[str] = Field(default_factory=list)
