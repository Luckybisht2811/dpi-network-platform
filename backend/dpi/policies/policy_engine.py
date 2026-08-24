from dpi.policies.blocklist import is_blocked


class PolicyEngine:
    def __init__(self):
        self.blocked_count = 0
        self.allowed_count = 0

    def evaluate(self, sni: str, flow: dict) -> str:
        """
        SNI aur flow ki information dekh kar decide karta hai:
        ALLOW ya BLOCK.
        Abhi sirf decision return karta hai — actual packet drop
        Phase 2b (pydivert) me karenge.
        """
        if is_blocked(sni):
            self.blocked_count += 1
            decision = "BLOCK"
        else:
            self.allowed_count += 1
            decision = "ALLOW"

        return decision

    def stats(self):
        return {
            "allowed": self.allowed_count,
            "blocked": self.blocked_count,
        }