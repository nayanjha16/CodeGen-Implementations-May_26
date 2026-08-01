"""Transfer-risk policy owned by this repository.

The constants are intentionally business-specific: a generic model cannot
infer them from a function signature, while repository retrieval can ground a
change in the exact policy already used by the application.
"""

from __future__ import annotations


def transfer_risk_score(
    amount: float,
    customer_tenure_days: int,
    destination_country: str,
    trusted_device: bool,
) -> float:
    """Calculate the repository's 0-100 cross-border transfer risk score."""
    high_risk_countries = {"IR", "KP", "SY"}
    score = 0.0
    if amount >= 250_000:
        score += 40
    elif amount >= 100_000:
        score += 25
    if customer_tenure_days < 30:
        score += 20
    if destination_country.strip().upper() in high_risk_countries:
        score += 30
    if not trusted_device:
        score += 15
    return min(score, 100.0)


def requires_step_up_auth(risk_score: float) -> bool:
    """Require an additional authentication challenge at score 50 or above."""
    return risk_score >= 50.0


def daily_transfer_limit(account_tier: str) -> float:
    """Return this repository's daily transfer limit for an account tier."""
    tier_limits = {
        "STANDARD": 100_000.0,
        "PREMIUM": 500_000.0,
        "PRIVATE": 2_000_000.0,
    }
    return tier_limits.get(account_tier.strip().upper(), 50_000.0)
