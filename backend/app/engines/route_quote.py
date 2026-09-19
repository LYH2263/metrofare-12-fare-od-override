from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_path


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    flat_prices: dict[tuple[str, str], float] | None = None,
) -> dict:
    """Shortest-path quote. A directed (start, end) hit in flat_prices overrides
    the segment-table fare; segment_fare always carries the table reference price."""
    path = shortest_path(edges, start, end)
    if path is None:
        return {
            "start": start,
            "end": end,
            "hops": None,
            "path": None,
            "fare": None,
            "segment_fare": None,
            "via_flat": False,
            "reachable": False,
        }
    hops = len(path) - 1
    segment_fare = fare_for_hops(hops, rules)
    flat = (flat_prices or {}).get((start, end))
    via_flat = flat is not None
    return {
        "start": start,
        "end": end,
        "hops": hops,
        "path": path,
        "fare": round(float(flat), 2) if via_flat else segment_fare,
        "segment_fare": segment_fare,
        "via_flat": via_flat,
        "reachable": True,
    }
