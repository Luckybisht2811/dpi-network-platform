from fastapi import APIRouter, HTTPException
from app.schemas.policy import DomainRequest
from dpi.policies.blocklist import get_blocklist, add_to_blocklist, remove_from_blocklist

router = APIRouter(prefix="/api/policy", tags=["Policy"])


@router.get("/blocklist")
def list_blocklist():
    """Current blocklist dikhata hai."""
    domains = get_blocklist()
    return {
        "count": len(domains),
        "domains": domains,
    }


@router.post("/blocklist")
def add_domain(request: DomainRequest):
    """Naya domain blocklist me add karta hai."""
    added = add_to_blocklist(request.domain)
    if not added:
        raise HTTPException(status_code=400, detail="Domain already blocked ya invalid hai")

    return {
        "message": f"'{request.domain}' blocklist me add ho gaya",
        "domains": get_blocklist(),
    }


@router.delete("/blocklist/{domain}")
def remove_domain(domain: str):
    """Domain ko blocklist se remove karta hai."""
    removed = remove_from_blocklist(domain)
    if not removed:
        raise HTTPException(status_code=404, detail="Domain blocklist me mila hi nahi")

    return {
        "message": f"'{domain}' blocklist se remove ho gaya",
        "domains": get_blocklist(),
    }