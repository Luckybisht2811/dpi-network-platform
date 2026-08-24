from fastapi import APIRouter
from app.core.redis import redis_client

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


@router.get("/")
def get_statistics():
    """
    Overall traffic statistics dikhata hai.
    """
    total_packets = redis_client.get("stats:total_packets") or 0
    total_bytes = redis_client.get("stats:total_bytes") or 0
    active_flows = len(redis_client.keys("flow:*"))

    return {
        "total_packets": int(total_packets),
        "total_bytes": int(total_bytes),
        "active_flows": active_flows,
    }