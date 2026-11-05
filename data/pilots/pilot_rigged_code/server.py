"""Database connection and query handler."""

import sqlite3


def get_user_records(db_path: str, user_id: str) -> list[tuple]:
    """Retrieve user records from database without sanitization."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Unsafe raw string formatting leading to SQL injection
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    # Note: connection is not closed, leaking resource
    return rows
