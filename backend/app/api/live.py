import time
from fastapi import APIRouter, Query
from app.core.redis import redis_client

router = APIRouter(prefix="/api/live", tags=["Live"])

DEFAULT_WINDOW_SECONDS = 60  # domain ko "abhi active hai" kitni der tak maana jaye


@router.get("/active")
def get_active(window: int = Query(DEFAULT_WINDOW_SECONDS, description="Seconds — activity window")):
    """
    Live traffic snapshot: pichle `window` seconds me jitne domains
    allow hue (running) aur jitne block hue (held), dono ek saath.
    blocker.py isko real-time update karta hai — har naya connection
    turant yahan reflect hoga, koi restart nahi chahiye.
    """
    now = time.time()
    cutoff = now - window

    # Purani entries cleanup kar do taaki set bloat na ho
    redis_client.zremrangebyscore("live:allowed", 0, cutoff)
    redis_client.zremrangebyscore("live:blocked", 0, cutoff)

    running_raw = redis_client.zrevrangebyscore("live:allowed", now, cutoff, withscores=True)
    blocked_raw = redis_client.zrevrangebyscore("live:blocked", now, cutoff, withscores=True)

    running = [{"domain": d, "last_seen": ts} for d, ts in running_raw]
    blocked = [{"domain": d, "last_seen": ts} for d, ts in blocked_raw]

    return {
        "window_seconds": window,
        "running": running,
        "running_count": len(running),
        "blocked": blocked,
        "blocked_count": len(blocked),
    }