"""Transaction processing for the demo BFSI sample repository."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Transaction:
    transaction_id: str
    from_account: str
    to_account: str
    amount: float
    currency: str = "INR"
    status: str = "completed"
    created_at: datetime = field(default_factory=datetime.utcnow)


class TransactionService:
    """Creates, reverses, and looks up money transfers between accounts."""

    def __init__(self, account_manager):
        self.account_manager = account_manager
        self._transactions: List[Transaction] = []

    def create_transaction(self, from_account: str, to_account: str, amount: float) -> Transaction:
        """Move funds from one account to another and record the transfer."""
        self.account_manager.withdraw(from_account, amount)
        self.account_manager.deposit(to_account, amount)
        txn = Transaction(
            transaction_id=str(uuid.uuid4()),
            from_account=from_account,
            to_account=to_account,
            amount=amount,
        )
        self._transactions.append(txn)
        return txn

    def reverse_transaction(self, transaction_id: str) -> Transaction:
        """Reverse a previously completed transaction, refunding the sender."""
        txn = self._find(transaction_id)
        self.account_manager.withdraw(txn.to_account, txn.amount)
        self.account_manager.deposit(txn.from_account, txn.amount)
        txn.status = "reversed"
        return txn

    def get_transaction_history(self, account_id: str, limit: int = 20) -> List[Transaction]:
        """Return the most recent transactions involving an account."""
        matches = [
            t for t in self._transactions
            if t.from_account == account_id or t.to_account == account_id
        ]
        return sorted(matches, key=lambda t: t.created_at, reverse=True)[:limit]

    def _find(self, transaction_id: str) -> Transaction:
        for txn in self._transactions:
            if txn.transaction_id == transaction_id:
                return txn
        raise KeyError(f"No such transaction: {transaction_id}")
