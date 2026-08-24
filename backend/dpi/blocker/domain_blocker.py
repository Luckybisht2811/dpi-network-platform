BLOCKED_DOMAINS = {
    "youtube.com",
    "facebook.com",
    "instagram.com",
}


def is_blocked_domain(sni):
    if not sni:
        return False

    sni = sni.lower().rstrip(".")

    for domain in BLOCKED_DOMAINS:
        if sni == domain or sni.endswith("." + domain):
            return True

    return False