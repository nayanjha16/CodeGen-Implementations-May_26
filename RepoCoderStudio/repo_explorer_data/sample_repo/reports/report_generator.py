"""Account statements and reporting for the demo BFSI sample repository."""

from __future__ import annotations

import csv
import io
from datetime import date
from typing import List


def calculate_interest(principal: float, annual_rate: float, days: int) -> float:
    """Compute simple interest earned on a balance over a number of days."""
    return principal * (annual_rate / 100) * (days / 365)


def generate_monthly_statement(account_id: str, transactions: List[dict], opening_balance: float) -> dict:
    """Build a monthly account statement summary from a list of transaction dicts."""
    total_debits = sum(t["amount"] for t in transactions if t.get("type") == "debit")
    total_credits = sum(t["amount"] for t in transactions if t.get("type") == "credit")
    closing_balance = opening_balance - total_debits + total_credits
    return {
        "account_id": account_id,
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "transaction_count": len(transactions),
    }


def export_to_csv(rows: List[dict]) -> str:
    """Serialize a list of row dictionaries into CSV text for download or archival."""
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def compute_average_daily_balance(daily_balances: List[float]) -> float:
    """Compute the average daily balance over a billing cycle, used for interest calculations."""
    if not daily_balances:
        return 0.0
    return sum(daily_balances) / len(daily_balances)
