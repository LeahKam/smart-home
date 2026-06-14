import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data/robots_db.db"
print(f"DB_PATH {DB_PATH}")
def parse_sql_query_response(sql_query_response) -> str:
    content = sql_query_response.choices[0].message.content
    if not content:
        raise ValueError("SQL query response was empty")
    content = content.strip()
    if content.startswith("```"):
        content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    payload = json.loads(content)
    sql_query = payload.get("sql_query")
    if not sql_query:
        raise ValueError("SQL query response did not include sql_query")
    return sql_query.strip()

def run_sql_query(sql_query: str) -> str:
    normalized_query = sql_query.strip().rstrip(";")
    lowered_query = normalized_query.lower()
    if ";" in normalized_query:
        raise ValueError("Only a single SQL statement is allowed")
    if not (lowered_query.startswith("select ") or lowered_query.startswith("with ")):
        raise ValueError("Only read-only SELECT queries are allowed")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(normalized_query)
        rows = [dict(row) for row in cursor.fetchall()]
    return json.dumps(
        {
            "sql_query": normalized_query,
            "rows": rows,
        },
        ensure_ascii=False,
        indent=2,
    )