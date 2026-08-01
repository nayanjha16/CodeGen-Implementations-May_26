"""Cross-border transfer orchestration for LedgerFlow.

This module intentionally composes APIs owned by other repository packages.
It gives Stage 4 a meaningful dependency graph and gives Stage 5 a realistic
"implement a change using existing repository contracts" scenario.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from audit.audit_logger import log_action
from policies.transfer_policy import (
    daily_transfer_limit,
    requires_step_up_auth,
    transfer_risk_score,
)
from transactions.fraud_detector import (
    calculate_risk_score,
    flag_suspicious_transaction,
)


@dataclass(frozen=True)
class TransferAssessment:
    """Decision returned before a cross-border transfer is submitted."""

    allowed: bool
    reason: str
    policy_risk_score: float
    fraud_risk_score: float
    step_up_auth_required: bool
    remaining_daily_limit: float
    audit_entry: Dict[str, Any]


def remaining_daily_limit(account_tier: str, transferred_today: float) -> float:
    """Return the non-negative amount still available for today's transfers."""

    return max(daily_transfer_limit(account_tier) - max(transferred_today, 0.0), 0.0)


def assess_cross_border_transfer(
    actor_id: str,
    transfer_id: str,
    amount: float,
    customer_tenure_days: int,
    destination_country: str,
    trusted_device: bool,
    account_tier: str,
    transferred_today: float,
    account_average_transaction: float,
    is_new_payee: bool,
) -> TransferAssessment:
    """Apply repository policy, fraud heuristics, limits, and audit rules."""

    policy_score = transfer_risk_score(
        amount,
        customer_tenure_days,
        destination_country,
        trusted_device,
    )
    fraud_score = calculate_risk_score(
        amount,
        account_average_transaction,
        is_new_payee,
    )
    remaining_limit = remaining_daily_limit(account_tier, transferred_today)

    if amount <= 0:
        allowed, reason = False, "invalid_amount"
    elif amount > remaining_limit:
        allowed, reason = False, "daily_limit_exceeded"
    elif policy_score >= 80.0 or flag_suspicious_transaction(fraud_score):
        allowed, reason = False, "manual_review_required"
    else:
        allowed, reason = True, "approved"

    step_up_required = allowed and (
        requires_step_up_auth(policy_score) or is_new_payee
    )
    audit_entry = log_action(
        actor_id,
        f"cross_border_transfer_{reason}",
        transfer_id,
    )
    return TransferAssessment(
        allowed=allowed,
        reason=reason,
        policy_risk_score=policy_score,
        fraud_risk_score=fraud_score,
        step_up_auth_required=step_up_required,
        remaining_daily_limit=remaining_limit,
        audit_entry=audit_entry,
    )


def should_notify_fraud_team(assessment: TransferAssessment) -> bool:
    """Notify fraud operations only for repository-defined manual reviews."""

    return assessment.reason == "manual_review_required"

