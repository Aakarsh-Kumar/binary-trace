# Dashboard and Database – Developer Guide

## 1. Overview

The Compliance Review System uses Streamlit for its reviewer interface and MySQL for persistent storage.

The dashboard allows reviewers to upload submissions, inspect compliance results, view skill retrieval information and examine review metrics.

The database stores submission information, skill executions, checklist verdicts, evidence verification results and reviewer feedback.

## 2. Dashboard Technology

The dashboard is developed using Streamlit, a Python framework for building interactive web applications.

**Main entry point:**

`src/compliance_review/dashboard/app.py`

**Dashboard pages:**

- `01_submission.py` – Submission and review interface.
- `02_skill_library.py` – Skill library interface.
- `03_metrics.py` – Evaluation metrics interface.

## 3. Dashboard Workflow

The dashboard supports the following workflow:

1. Reviewer opens the application.
2. Reviewer uploads a student submission.
3. The submission is processed by the backend.
4. The review pipeline generates checklist verdicts.
5. The reviewer examines findings and supporting evidence.
6. The reviewer can inspect evaluation metrics and review information.

## 4. Database Technology

The system uses MySQL 8.0 with SQLAlchemy Core for database access and Alembic for schema migrations.

**Main implementation files:**

- `src/compliance_review/db/engine.py`
- `src/compliance_review/db/tables.py`
- `src/compliance_review/db/repository.py`

The repository module provides database operations used by the application.

## 5. Database Tables

The system uses seven main tables.

| Table | Responsibility |
|---|---|
| submissions | Stores submission metadata |
| retrieval_events | Stores capability and retrieval information |
| skill_executions | Stores individual skill execution records |
| checklist_verdicts | Stores checklist results |
| evidence_verifications | Stores evidence verification outcomes |
| reviewer_feedback | Stores reviewer decisions |
| audit_log | Maintains an append-only activity history |

## 6. Data Flow

The database workflow follows this sequence:

1. Submission metadata is stored in the submissions table.
2. Retrieval decisions are recorded in retrieval_events.
3. Individual skill executions are stored in skill_executions.
4. Checklist results are stored in checklist_verdicts.
5. Evidence verification outcomes are stored in evidence_verifications.
6. Reviewer actions are stored in reviewer_feedback.
7. Important application activities are recorded in audit_log.

## 7. Audit Logging

The audit_log table maintains an append-only record of important activities.

The application database user is granted INSERT and SELECT permissions, while UPDATE and DELETE permissions are revoked.

This helps preserve the history of reviewer and system activities.

## 8. Running the Dashboard

From the project root, run:

```bash
streamlit run src/compliance_review/dashboard/app.py
```

Alternatively:

```bash
python scripts/run_dashboard.py
```

Ensure that the required environment configuration, database connection and project dependencies are available before starting the application.

## 9. Conclusion

The dashboard and database components provide the user interaction and persistent storage layers of the Compliance Review System.

Streamlit provides the reviewer interface, while MySQL maintains structured review records and audit information.

Together, these components support transparent and traceable assignment compliance reviews.
