# LedgerFlow Sample Repository

LedgerFlow is a synthetic but internally coherent BFSI codebase used to
demonstrate RepoCoderStudio without exposing private source code. It contains
Python services, selected Java migrations, repository-specific business
policies, and real cross-module dependencies.

## Why this repository is the primary mentor demo

- The hidden transfer policy gives RAG information the base model cannot know.
- Python and Java counterparts exercise bilingual indexing and translation.
- `transfers/transfer_orchestrator.py` composes policy, fraud, limits, and
  auditing APIs, enabling dependency-aware retrieval rather than isolated
  function lookup.
- Every mentor-facing query has labelled retrieval ground truth.
- Generated policy code can be checked using deterministic Python and Java
  Docker cases.
- The repository is small enough to rebuild its index during a live demo.

## Architecture

```text
transfers/transfer_orchestrator.py
    ├── policies/transfer_policy.py
    ├── transactions/fraud_detector.py
    └── audit/audit_logger.py

transactions/transaction_service.py
    └── account-manager interface
```

Other packages cover accounts, KYC, cards, loans, AML screening,
notifications, reports, support routing, currency, and validation.

## Best demonstration

Use the UI preset **Repository policy → Python (best RAG proof)** and run all
four arms:

1. baseline without RAG;
2. baseline with RAG;
3. fine-tuned without RAG;
4. fine-tuned with RAG.

The prompt does not reveal thresholds or weights. A correct RAG answer should
recover the repository's amount thresholds, risk weights, country set, and
score cap from `policies/transfer_policy.py`.

