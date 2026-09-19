import sqlite3
from datetime import datetime, timezone


class DuplicateFlatFare(Exception):
    """Raised when a directed (start, end) pair already has a flat fare."""


def list_all(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT id, start_code, end_code, price, created_at FROM flat_fares ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def get_by_pair(conn: sqlite3.Connection, start: str, end: str) -> dict | None:
    row = conn.execute(
        "SELECT id, start_code, end_code, price, created_at FROM flat_fares "
        "WHERE start_code=? AND end_code=?",
        (start, end),
    ).fetchone()
    return dict(row) if row else None


def as_price_map(conn: sqlite3.Connection) -> dict[tuple[str, str], float]:
    return {(r["start_code"], r["end_code"]): r["price"] for r in list_all(conn)}


def insert(conn: sqlite3.Connection, start: str, end: str, price: float) -> int:
    now = datetime.now(timezone.utc).isoformat()
    try:
        cur = conn.execute(
            "INSERT INTO flat_fares(start_code, end_code, price, created_at) VALUES (?,?,?,?)",
            (start, end, price, now),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise DuplicateFlatFare(f"{start}->{end}")
    return int(cur.lastrowid)


def delete(conn: sqlite3.Connection, flat_id: int) -> bool:
    cur = conn.execute("DELETE FROM flat_fares WHERE id=?", (flat_id,))
    conn.commit()
    return cur.rowcount > 0
