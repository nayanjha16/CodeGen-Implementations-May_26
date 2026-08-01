"""Fraud detection heuristics for the demo BFSI sample repository."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List


def calculate_risk_score(amount: float, account_avg_transaction: float, is_new_payee: bool) -> float:
    """Compute a 0-100 fraud risk score for a transaction based on amount and payee history."""
    score = 0.0
    if account_avg_transaction > 0:
        ratio = amount / account_avg_transaction
        score += min(ratio * 10, 60)
    if is_new_payee:
        score += 25
    if amount > 100_000:
        score += 15
    return min(score, 100.0)


def flag_suspicious_transaction(risk_score: float, threshold: float = 70.0) -> bool:
    """Decide whether a transaction should be flagged for manual fraud review."""
    return risk_score >= threshold


def check_velocity_limit(recent_transaction_times: List[datetime], window_minutes: int = 10, max_count: int = 5) -> bool:
    """Return True if too many transactions have occurred within a short time window (velocity fraud check)."""
    if not recent_transaction_times:
        return False
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    recent_count = sum(1 for t in recent_transaction_times if t >= cutoff)
    return recent_count > max_count


def detect_round_amount_pattern(amounts: List[float]) -> bool:
    """Flag a suspicious pattern of suspiciously round transaction amounts, often seen in structuring/smurfing."""
    round_count = sum(1 for a in amounts if a % 1000 == 0 and a > 0)
    return len(amounts) > 0 and (round_count / len(amounts)) > 0.6
