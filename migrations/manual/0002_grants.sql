-- Manual DBA step per ARCHITECTURE.md §4.7 (Decision D-008)
-- Do NOT execute this from Alembic migrations.
-- Run once as MySQL DBA / root:

REVOKE UPDATE, DELETE ON compliance_review.audit_log FROM 'app_user'@'%';
GRANT INSERT, SELECT ON compliance_review.audit_log TO 'app_user'@'%';
FLUSH PRIVILEGES;
