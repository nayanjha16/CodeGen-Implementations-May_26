"""Account lifecycle management for the demo BFSI sample repository.

This is a demo/example codebase built for showcasing RepoCoder Studio's
Stage 4/5 repository-aware RAG. It is not part of your original Stage 4
submission -- swap it out for your real Stage 4 sample_repo, or your
own project, whenever you like.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Account:
    account_id: str
    customer_id: str
    balance: float = 0.0
    currency: str = "INR"
    status: str = "active"
    opened_on: datetime = field(default_factory=datetime.utcnow)


class AccountManager:
    """Handles opening, closing, freezing, and balance operations for
    customer bank accounts."""

    def __init__(self):
        self._accounts: dict[str, Account] = {}

    def create_account(self, account_id: str, customer_id: str, currency: str = "INR") -> Account:
        """Open a new bank account for a customer with a zero starting balance."""
        account = Account(account_id=account_id, customer_id=customer_id, currency=currency)
        self._accounts[account_id] = account
        return account

    def get_balance(self, account_id: str) -> float:
        """Return the current balance for an account."""
        return self._require(account_id).balance

    def deposit(self, account_id: str, amount: float) -> float:
        """Credit an account with a deposit and return the new balance."""
        account = self._require(account_id)
        account.balance += amount
        return account.balance

    def withdraw(self, account_id: str, amount: float) -> float:
        """Debit an account with a withdrawal, raising if funds are insufficient."""
        account = self._require(account_id)
        if account.balance < amount:
            raise ValueError(f"Insufficient funds in account {account_id}")
        account.balance -= amount
        return account.balance

    def freeze_account(self, account_id: str, reason: str) -> None:
        """Freeze an account, blocking withdrawals, typically for fraud review."""
        self._require(account_id).status = "frozen"

    def close_account(self, account_id: str) -> None:
        """Permanently close an account. Balance must be zero first."""
        account = self._require(account_id)
        if account.balance != 0:
            raise ValueError("Cannot close an account with a non-zero balance")
        account.status = "closed"

    def _require(self, account_id: str) -> Account:
        if account_id not in self._accounts:
            raise KeyError(f"No such account: {account_id}")
        return self._accounts[account_id]
