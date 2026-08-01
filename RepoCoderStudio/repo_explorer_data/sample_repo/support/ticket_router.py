"""Customer support ticket triage for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations

_URGENT_KEYWORDS = {"fraud", "unauthorized", "blocked", "stolen", "lost card"}
_DEPARTMENT_BY_CATEGORY = {
    "fraud": "Fraud & Security",
    "loan": "Loans",
    "card": "Cards",
    "account": "Retail Banking",
}


def classify_ticket_priority(subject: str, body: str) -> str:
    """Classify a support ticket as HIGH, MEDIUM, or LOW priority from its text."""
    text = f"{subject} {body}".lower()
    if any(keyword in text for keyword in _URGENT_KEYWORDS):
        return "HIGH"
    if "urgent" in text or "asap" in text:
        return "MEDIUM"
    return "LOW"


def route_to_department(category: str) -> str:
    """Route a ticket category to the department responsible for handling it."""
    return _DEPARTMENT_BY_CATEGORY.get(category.lower(), "General Support")


def estimate_resolution_time(priority: str) -> int:
    """Estimate resolution time in hours based on ticket priority."""
    return {"HIGH": 2, "MEDIUM": 24, "LOW": 72}.get(priority.upper(), 72)
