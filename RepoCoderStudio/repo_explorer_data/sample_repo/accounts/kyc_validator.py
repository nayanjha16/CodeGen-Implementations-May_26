"""Customer identity verification (KYC) for the demo BFSI sample repository."""

from __future__ import annotations

import re


def validate_pan(pan_number: str) -> bool:
    """Check whether a string matches the Indian PAN card format (5 letters, 4 digits, 1 letter)."""
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", pan_number.strip().upper()))


def validate_aadhaar(aadhaar_number: str) -> bool:
    """Check whether a string is a plausible 12-digit Aadhaar number."""
    digits = aadhaar_number.replace(" ", "")
    return digits.isdigit() and len(digits) == 12


def verify_identity(pan_number: str, aadhaar_number: str, full_name: str) -> dict:
    """Run full KYC identity verification, combining PAN and Aadhaar checks."""
    pan_ok = validate_pan(pan_number)
    aadhaar_ok = validate_aadhaar(aadhaar_number)
    name_ok = bool(full_name and full_name.strip())
    return {
        "verified": pan_ok and aadhaar_ok and name_ok,
        "pan_valid": pan_ok,
        "aadhaar_valid": aadhaar_ok,
        "name_provided": name_ok,
    }


def mask_pan(pan_number: str) -> str:
    """Mask a PAN number for display, keeping only the last 4 characters visible."""
    pan_number = pan_number.strip().upper()
    if len(pan_number) < 4:
        return "*" * len(pan_number)
    return "*" * (len(pan_number) - 4) + pan_number[-4:]
