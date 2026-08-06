"""Catalog of GoF patterns, SOLID principles, domains, and train/test splits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Kind = Literal["design_pattern", "solid", "combo"]
Category = Literal["creational", "structural", "behavioral", "solid", "combo"]

SEED = 42

# Aligned with agent/prompts.py KNOWN_PATTERNS
PATTERNS: list[dict[str, str]] = [
    {"id": "singleton", "label": "singleton", "category": "creational"},
    {"id": "factory", "label": "factory", "category": "creational"},
    {"id": "abstract_factory", "label": "abstract factory", "category": "creational"},
    {"id": "builder", "label": "builder", "category": "creational"},
    {"id": "prototype", "label": "prototype", "category": "creational"},
    {"id": "adapter", "label": "adapter", "category": "structural"},
    {"id": "bridge", "label": "bridge", "category": "structural"},
    {"id": "composite", "label": "composite", "category": "structural"},
    {"id": "decorator", "label": "decorator", "category": "structural"},
    {"id": "facade", "label": "facade", "category": "structural"},
    {"id": "flyweight", "label": "flyweight", "category": "structural"},
    {"id": "proxy", "label": "proxy", "category": "structural"},
    {"id": "chain_of_responsibility", "label": "chain of responsibility", "category": "behavioral"},
    {"id": "command", "label": "command", "category": "behavioral"},
    {"id": "interpreter", "label": "interpreter", "category": "behavioral"},
    {"id": "iterator", "label": "iterator", "category": "behavioral"},
    {"id": "mediator", "label": "mediator", "category": "behavioral"},
    {"id": "memento", "label": "memento", "category": "behavioral"},
    {"id": "observer", "label": "observer", "category": "behavioral"},
    {"id": "state", "label": "state", "category": "behavioral"},
    {"id": "strategy", "label": "strategy", "category": "behavioral"},
    {"id": "template_method", "label": "template method", "category": "behavioral"},
    {"id": "visitor", "label": "visitor", "category": "behavioral"},
]

SOLID: list[dict[str, str]] = [
    {"id": "srp", "label": "srp", "category": "solid"},
    {"id": "ocp", "label": "ocp", "category": "solid"},
    {"id": "lsp", "label": "lsp", "category": "solid"},
    {"id": "isp", "label": "isp", "category": "solid"},
    {"id": "dip", "label": "dip", "category": "solid"},
]

# Combo scenarios: pattern applied while respecting a SOLID principle
COMBOS: list[dict[str, str]] = [
    {"id": "strategy_ocp", "label": "strategy+ocp", "category": "combo", "pattern": "strategy", "solid": "ocp"},
    {"id": "factory_dip", "label": "factory+dip", "category": "combo", "pattern": "factory", "solid": "dip"},
    {"id": "observer_srp", "label": "observer+srp", "category": "combo", "pattern": "observer", "solid": "srp"},
    {"id": "decorator_ocp", "label": "decorator+ocp", "category": "combo", "pattern": "decorator", "solid": "ocp"},
    {"id": "adapter_isp", "label": "adapter+isp", "category": "combo", "pattern": "adapter", "solid": "isp"},
]

# ~48 domains; last 8 are held out entirely for the test split
ALL_DOMAINS: list[str] = [
    "logging",
    "payments",
    "notifications",
    "cache",
    "auth",
    "inventory",
    "chat",
    "sensors",
    "widgets",
    "storage",
    "metrics",
    "scheduling",
    "cart",
    "game",
    "config",
    "http",
    "email",
    "sms",
    "queue",
    "database",
    "search",
    "report",
    "billing",
    "shipping",
    "tax",
    "discount",
    "analytics",
    "streaming",
    "backup",
    "sync",
    "editor",
    "canvas",
    "audio",
    "video",
    "map",
    "calendar",
    "todo",
    "notes",
    "session",
    "plugin",
    # Held-out test domains (disjoint from train)
    "wallet",
    "ticket",
    "booking",
    "review",
    "feed",
    "comment",
    "profile",
    "license",
]

TEST_DOMAINS: list[str] = ALL_DOMAINS[-8:]
TRAIN_DOMAINS: list[str] = ALL_DOMAINS[:-8]

TIERS: list[str] = ["minimal", "logging", "errors"]


@dataclass(frozen=True)
class DomainContext:
    """Nouns / identifiers derived from a domain name for code generation."""

    domain: str
    pascal: str
    snake: str
    entity: str
    entity_snake: str
    service: str
    service_snake: str

    @classmethod
    def from_domain(cls, domain: str) -> DomainContext:
        pascal = "".join(p.capitalize() for p in domain.replace("-", "_").split("_"))
        snake = domain.replace("-", "_").lower()
        return cls(
            domain=domain,
            pascal=pascal,
            snake=snake,
            entity=f"{pascal}Item",
            entity_snake=f"{snake}_item",
            service=f"{pascal}Service",
            service_snake=f"{snake}_service",
        )


def slug(label: str) -> str:
    return label.replace(" ", "_").replace("+", "_").lower()
