"""Loan eligibility scoring for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations


def calculate_eligible_amount(monthly_income: float, existing_emis: float, credit_score: int) -> float:
    """Estimate the maximum loan amount a customer is eligible for, based on income headroom and credit score."""
    disposable_income = monthly_income - existing_emis
    if disposable_income <= 0:
        return 0.0
    multiplier = 60 if credit_score >= 750 else 48 if credit_score >= 650 else 24
    return round(disposable_income * multiplier, 2)


def check_minimum_credit_score(credit_score: int, loan_type: str) -> bool:
    """Check whether a credit score meets the minimum bar for the given loan type."""
    thresholds = {"personal": 650, "home": 700, "vehicle": 600, "education": 550}
    return credit_score >= thresholds.get(loan_type.lower(), 700)


def debt_to_income_ratio(monthly_income: float, total_emis: float) -> float:
    """Compute a customer's debt-to-income ratio as a percentage."""
    if monthly_income <= 0:
        return 100.0
    return round((total_emis / monthly_income) * 100, 2)
