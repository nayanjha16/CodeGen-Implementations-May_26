"""Loan repayment calculations for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations

from typing import List


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Compute the fixed monthly EMI for a loan given principal, annual interest rate, and tenure."""
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return round(principal / tenure_months, 2)
    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    return round(emi, 2)


def generate_amortization_schedule(principal: float, annual_rate: float, tenure_months: int) -> List[dict]:
    """Build a month-by-month amortization schedule (principal/interest split, closing balance)."""
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100
    balance = principal
    schedule = []
    for month in range(1, tenure_months + 1):
        interest_component = round(balance * monthly_rate, 2)
        principal_component = round(emi - interest_component, 2)
        balance = round(balance - principal_component, 2)
        schedule.append({
            "month": month,
            "emi": emi,
            "principal_component": principal_component,
            "interest_component": interest_component,
            "closing_balance": max(balance, 0.0),
        })
    return schedule


def calculate_total_interest(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Compute the total interest paid over the full tenure of a loan."""
    emi = calculate_emi(principal, annual_rate, tenure_months)
    return round(emi * tenure_months - principal, 2)
