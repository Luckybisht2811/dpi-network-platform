import json
from fastapi import APIRouter, Query
from app.core.redis import redis_client

router = APIRouter(prefix="/api/flows", tags=["Flows"])


@router.get("/")
def get_flows(
    limit: int = Query(50, description="Max number of flows to return"),
    only_blocked: bool = Query(False, description="Sirf blocked flows dikhao"),
):
    """
    Redis me stored saare active flows return karta hai.
    """
    keys = redis_client.keys("flow:*")
    flows = []

    for key in keys[:limit * 3]:  # thoda buffer rakhte hain filtering ke liye
        raw = redis_client.get(key)
        if not raw:
            continue

        flow = json.loads(raw)

        if only_blocked and flow.get("decision") != "BLOCK":
            continue

        flows.append(flow)

        if len(flows) >= limit:
            break

    return {
        "count": len(flows),
        "flows": flows,
    }


@router.get("/{client_ip}")
def get_flows_by_client(client_ip: str):
    """
    Ek specific client IP ke saare flows return karta hai.
    """
    keys = redis_client.keys(f"flow:{client_ip}:*")
    flows = []

    for key in keys:
        raw = redis_client.get(key)
        if raw:
            flows.append(json.loads(raw))

    return {
        "client_ip": client_ip,
        "count": len(flows),
        "flows": flows,
    }