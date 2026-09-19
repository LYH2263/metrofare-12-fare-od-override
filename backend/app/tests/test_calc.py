import sqlite3

import pytest

from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_hops, shortest_path
from app.engines.route_quote import quote_route
from app.repositories import flat_fares as flat_repo

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_path_a1_b2():
    assert shortest_path(EDGES, "A1", "B2") == ["A1", "A2", "B1", "B2"]


def test_path_unreachable():
    assert shortest_path(EDGES, "A1", "ZZ") is None
    assert shortest_hops(EDGES, "A1", "ZZ") is None


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["hops"] == 3 and q["fare"] == 4.0
    assert q["via_flat"] is False and q["segment_fare"] == 4.0
    assert q["path"] == ["A1", "A2", "B1", "B2"]


def test_quote_flat_hit():
    q = quote_route(EDGES, "A1", "B2", RULES, {("A1", "B2"): 2.5})
    assert q["fare"] == 2.5 and q["via_flat"] is True
    assert q["segment_fare"] == 4.0
    assert q["hops"] == 3 and q["path"] == ["A1", "A2", "B1", "B2"]


def test_quote_flat_is_directed():
    q = quote_route(EDGES, "B2", "A1", RULES, {("A1", "B2"): 2.5})
    assert q["via_flat"] is False and q["fare"] == 4.0


def test_quote_flat_miss_other_pair():
    q = quote_route(EDGES, "A1", "A3", RULES, {("A1", "B2"): 2.5})
    assert q["via_flat"] is False and q["fare"] == 3.0


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute(
        "CREATE TABLE flat_fares(id INTEGER PRIMARY KEY, start_code TEXT NOT NULL, "
        "end_code TEXT NOT NULL, price REAL NOT NULL, created_at TEXT, "
        "UNIQUE(start_code, end_code))"
    )
    yield c
    c.close()


def test_repo_duplicate_rejected(conn):
    flat_repo.insert(conn, "A1", "B2", 2.5)
    with pytest.raises(flat_repo.DuplicateFlatFare):
        flat_repo.insert(conn, "A1", "B2", 3.0)
    # reverse direction is a different pair and is allowed
    flat_repo.insert(conn, "B2", "A1", 9.0)


def test_repo_delete_restores_segment_lookup(conn):
    flat_id = flat_repo.insert(conn, "A1", "B2", 2.5)
    assert flat_repo.as_price_map(conn) == {("A1", "B2"): 2.5}
    assert flat_repo.delete(conn, flat_id) is True
    assert flat_repo.as_price_map(conn) == {}
    assert flat_repo.delete(conn, flat_id) is False
