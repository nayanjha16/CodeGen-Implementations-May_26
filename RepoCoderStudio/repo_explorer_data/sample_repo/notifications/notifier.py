"""Customer notification delivery for the demo BFSI sample repository."""

from __future__ import annotations

from typing import Literal


class Notifier:
    """Sends transactional alerts to customers over SMS, email, or push."""

    def send_sms_alert(self, phone_number: str, message: str) -> dict:
        """Send a short SMS alert to a customer's registered mobile number."""
        return {"channel": "sms", "to": phone_number, "message": message[:160], "status": "sent"}

    def send_email_alert(self, email: str, subject: str, body: str) -> dict:
        """Send a transactional email alert, e.g. for a debit or credit notification."""
        return {"channel": "email", "to": email, "subject": subject, "status": "sent"}

    def send_push_notification(self, device_token: str, title: str, body: str) -> dict:
        """Send a mobile push notification to a customer's registered device."""
        return {"channel": "push", "to": device_token, "title": title, "status": "sent"}

    def send_fraud_alert(self, phone_number: str, email: str, transaction_id: str) -> None:
        """Notify a customer across all channels when a transaction is flagged as suspicious."""
        message = f"Suspicious activity detected on transaction {transaction_id}. Reply STOP to block."
        self.send_sms_alert(phone_number, message)
        self.send_email_alert(email, "Security Alert", message)


def format_alert_message(event_type: Literal["debit", "credit", "fraud"], amount: float, balance: float) -> str:
    """Build a human-readable alert message string for a transaction event."""
    if event_type == "debit":
        return f"Rs.{amount:.2f} debited. Available balance: Rs.{balance:.2f}"
    if event_type == "credit":
        return f"Rs.{amount:.2f} credited. Available balance: Rs.{balance:.2f}"
    return f"Suspicious transaction of Rs.{amount:.2f} flagged for review."
