# LedgerFlow — Migration Status

LedgerFlow is the Stage 4/5 demo repository: a synthetic BFSI codebase
currently migrating from Python to Java. That framing matches the capstone's
legacy-modernization use case and gives repository understanding and RAG one
coherent job.

## Already migrated to Java (3 of 16 business modules)

| Python | Java |
|---|---|
| `transactions/fraud_detector.py` | `transactions/FraudDetector.java` |
| `accounts/kyc_validator.py` | `accounts/KycValidator.java` |
| `policies/transfer_policy.py` | `policies/TransferPolicy.java` |

Each Java file is a faithful, `javac`-verified translation of its Python
counterpart. These are safety-critical modules where keeping policy behavior
identical across languages matters.

## Not yet migrated (13 modules)

The Python-only backlog is:

- `accounts/account_manager.py`
- `notifications/notifier.py`
- `reports/report_generator.py`
- `transactions/transaction_service.py`
- `transfers/transfer_orchestrator.py`
- `utils/currency_utils.py`
- `utils/validators.py`
- `loans/loan_calculator.py`
- `loans/loan_eligibility.py`
- `cards/card_manager.py`
- `compliance/aml_screening.py`
- `audit/audit_logger.py`
- `support/ticket_router.py`

Package markers such as `__init__.py` are intentionally excluded from the
migration denominator.

## Why this matters for Stage 4/5

- Stage 4 can answer how much of the repository is migrated and what remains.
- T3 Python-to-Java generation can retrieve this team's three prior Java
  translations as repository style references.
- `transfers/transfer_orchestrator.py` creates a real dependency graph across
  transfer policy, fraud scoring, daily limits, and audit logging.
- Stage 5 can retrieve repository context and similar validated-corpus
  examples as separately labelled evidence.
