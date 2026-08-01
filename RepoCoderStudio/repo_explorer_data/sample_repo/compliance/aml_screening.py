"""Anti-money-laundering (AML) screening heuristics for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations

from typing import List


def screen_against_watchlist(full_name: str, watchlist: List[str]) -> bool:
    """Check whether a customer's name matches (case-insensitively) an entry on a sanctions watchlist."""
    normalized = full_name.strip().lower()
    return any(normalized == entry.strip().lower() for entry in watchlist)


def calculate_transaction_risk_band(amount: float, country_risk_score: int) -> str:
    """Classify a transaction into a risk band based on amount and destination-country risk score."""
    score = country_risk_score + (20 if amount > 1_000_000 else 10 if amount > 100_000 else 0)
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def flag_structuring_pattern(transaction_amounts: List[float], threshold: float = 1_000_000.0) -> bool:
    """Flag a suspicious pattern of transactions kept just under a reporting threshold (structuring)."""
    near_threshold = [a for a in transaction_amounts if threshold * 0.9 <= a < threshold]
    return len(near_threshold) >= 3
