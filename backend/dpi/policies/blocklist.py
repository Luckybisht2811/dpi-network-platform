from app.core.redis import redis_client

REDIS_BLOCKLIST_KEY = "policy:blocklist"

# Pehli baar system chalane par default domains seed karne ke liye
DEFAULT_BLOCKED_DOMAINS = [
    "netflix.com",
    "nflxso.net",
    "nflxext.com",
    "nflximg.net",
    "nflxvideo.net",
    "wikipedia.org",
]


def seed_default_blocklist():
    """Agar Redis me blocklist khaali hai, to default domains daal do."""
    if redis_client.scard(REDIS_BLOCKLIST_KEY) == 0:
        for domain in DEFAULT_BLOCKED_DOMAINS:
            redis_client.sadd(REDIS_BLOCKLIST_KEY, domain.lower())


def is_blocked(hostname: str) -> bool:
    """
    Check karta hai ki diya gaya hostname blocked list me hai ya nahi.
    Ab ye Redis se live check karta hai — koi bhi update turant reflect hoga.
    """
    if not hostname:
        return False

    hostname = hostname.lower()
    blocked_domains = redis_client.smembers(REDIS_BLOCKLIST_KEY)

    for blocked in blocked_domains:
        if blocked in hostname:
            return True

    return False


def get_blocklist():
    """Poori blocklist return karta hai (sorted)."""
    return sorted(redis_client.smembers(REDIS_BLOCKLIST_KEY))


def add_to_blocklist(domain: str) -> bool:
    """Naya domain add karta hai. True return karega agar naya add hua."""
    domain = domain.lower().strip()
    if not domain:
        return False
    result = redis_client.sadd(REDIS_BLOCKLIST_KEY, domain)
    return result == 1  # 1 matlab naya add hua, 0 matlab already tha


def remove_from_blocklist(domain: str) -> bool:
    """Domain remove karta hai. True return karega agar mila aur remove hua."""
    domain = domain.lower().strip()
    result = redis_client.srem(REDIS_BLOCKLIST_KEY, domain)
    return result == 1