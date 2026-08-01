"""Audit trail logging for the demo BFSI sample repository.

Not yet migrated to Java -- see the repo-level migration note in
repo_explorer_data/sample_repo/MIGRATION.md.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


_REDACTED_FIELDS = {"pan_number", "aadhaar_number", "card_number", "password"}


def log_action(actor_id: str, action: str, resource_id: str) -> Dict[str, Any]:
    """Build an audit log entry for an actor performing an action on a resource."""
    return {
        "actor_id": actor_id,
        "action": action,
        "resource_id": resource_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


def get_audit_trail(resource_id: str, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return every logged action for a given resource, in the order they were recorded."""
    return [entry for entry in logs if entry.get("resource_id") == resource_id]


def redact_sensitive_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of a record with sensitive fields masked before it can be logged or displayed."""
    return {
        key: ("***REDACTED***" if key in _REDACTED_FIELDS else value)
        for key, value in record.items()
    }
