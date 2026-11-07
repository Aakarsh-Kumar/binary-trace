# Compliance Review System

Local-first, capability-gated, evidence-verified compliance review system for student submissions.

## Manual Setup Steps

### Audit Log Append-Only Grants (D-008)
Per `ARCHITECTURE.md §4.7`, run `migrations/manual/0002_grants.sql` as a MySQL DBA:

```sql
REVOKE UPDATE, DELETE ON compliance_review.audit_log FROM 'app_user'@'%';
GRANT INSERT, SELECT ON compliance_review.audit_log TO 'app_user'@'%';
```
This grant is manual and is NOT executed by Alembic.


## Streamlit Dashboard

Run the interactive review dashboard (ARCHITECTURE.md §10):

```bash
streamlit run src/compliance_review/dashboard/app.py
```

Or using the Python wrapper script:

```bash
python scripts/run_dashboard.py
```
