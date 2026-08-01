"""Debit/credit card lifecycle management for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations


def validate_card_number(card_number: str) -> bool:
    """Validate a card number's check digit using the Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def issue_card(customer_id: str, card_type: str) -> dict:
    """Issue a new card record for a customer (card number generation is out of scope for this demo)."""
    return {
        "customer_id": customer_id,
        "card_type": card_type,
        "status": "ACTIVE",
        "daily_limit": 50000.0,
    }


def block_card(card_number: str, reason: str) -> dict:
    """Block a card, recording the reason for the block."""
    return {"card_number": card_number, "status": "BLOCKED", "reason": reason}


def set_transaction_limit(card: dict, daily_limit: float) -> dict:
    """Update a card's daily transaction limit."""
    card = dict(card)
    card["daily_limit"] = daily_limit
    return card
