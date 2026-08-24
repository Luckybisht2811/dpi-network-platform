import json
from fastapi import APIRouter, Query
from app.core.redis import redis_client

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/blocked-events")
def get_blocked_events(limit: int = Query(50, description="Kitne recent events chahiye")):
    """Recent blocked connections ki list."""
    raw_events = redis_client.lrange("blocked_events", 0, limit - 1)
    events = [json.loads(e) for e in raw_events]

    return {
        "count": len(events),
        "events": events,
    }


@router.get("/summary")
def get_alerts_summary():
    """Blocked traffic ka summary — total, by domain, by client."""
    total_blocked = redis_client.get("stats:total_blocked") or 0
    by_domain = redis_client.hgetall("stats:blocked_by_domain")
    by_client = redis_client.hgetall("stats:blocked_by_client")

    return {
        "total_blocked": int(total_blocked),
        "blocked_by_domain": {k: int(v) for k, v in by_domain.items()},
        "blocked_by_client": {k: int(v) for k, v in by_client.items()},
    }