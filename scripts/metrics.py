"""Simple in-memory metrics."""
_queries = 0
_costs = 0.0
_escalations = 0


def record_query(cost: float, escalated: bool):
    global _queries, _costs, _escalations
    _queries += 1
    _costs += cost
    if escalated:
        _escalations += 1


def get_metrics():
    rate = _escalations / max(_queries, 1) * 100
    return {
        "total_queries": _queries,
        "total_cost_usd": round(_costs, 4),
        "escalation_rate": f"{rate:.1f}%",
        "avg_cost_per_query": round(_costs / max(_queries, 1), 4)
    }
