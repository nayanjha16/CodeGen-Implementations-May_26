"""General-purpose input validators for the demo BFSI sample repository."""

from __future__ import annotations

import re


def validate_email(email: str) -> bool:
    """Check whether a string is a syntactically valid email address."""
    pattern = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_phone_number(phone: str) -> bool:
    """Check whether a string is a valid 10-digit Indian mobile phone number."""
    digits = re.sub(r"\D", "", phone)
    return len(digits) == 10 and digits[0] in "6789"


def validate_ifsc_code(ifsc: str) -> bool:
    """Check whether a string matches the Indian bank IFSC code format (4 letters, 0, 6 alphanumeric)."""
    return bool(re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc.strip().upper()))


def validate_account_number(account_number: str) -> bool:
    """Check whether a string is a plausible bank account number (9 to 18 digits)."""
    digits = account_number.strip()
    return digits.isdigit() and 9 <= len(digits) <= 18
