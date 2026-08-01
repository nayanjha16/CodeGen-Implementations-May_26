"""Currency and amount formatting utilities for the demo BFSI sample repository."""

from __future__ import annotations

_STATIC_RATES = {
    ("USD", "INR"): 83.2,
    ("INR", "USD"): 1 / 83.2,
    ("EUR", "INR"): 90.5,
    ("INR", "EUR"): 1 / 90.5,
}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert an amount between two currencies using a static exchange-rate table."""
    if from_currency == to_currency:
        return amount
    rate = _STATIC_RATES.get((from_currency, to_currency))
    if rate is None:
        raise ValueError(f"No exchange rate available for {from_currency} -> {to_currency}")
    return round(amount * rate, 2)


def format_amount(amount: float, currency: str = "INR") -> str:
    """Format a numeric amount as a display string with currency symbol and thousands separators."""
    symbols = {"INR": "\u20b9", "USD": "$", "EUR": "\u20ac"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"


def round_to_paise(amount: float) -> float:
    """Round a rupee amount to the nearest whole paise (2 decimal places)."""
    return round(amount, 2)


def paise_to_rupees(paise: int) -> float:
    """Convert an integer paise amount into a rupee float."""
    return paise / 100.0
