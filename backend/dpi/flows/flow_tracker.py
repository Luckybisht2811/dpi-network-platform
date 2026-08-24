import time
import json
from app.core.redis import redis_client


class FlowTracker:
    def __init__(self):
        self.flows = {}

    def _identify_client_server(self, flow):
        """
        Decide karta hai kaun client hai kaun server.
        Convention: port 443 wala server hai, doosra client hai.
        """
        src = (flow["src_ip"], flow["src_port"])
        dst = (flow["dst_ip"], flow["dst_port"])

        if flow["dst_port"] == 443:
            return src, dst   # (client, server)
        elif flow["src_port"] == 443:
            return dst, src   # (client, server)
        else:
            # fallback: dono me se chhota port wala server maan lo
            return (src, dst) if src[1] > dst[1] else (dst, src)

    def _make_key(self, client, server, protocol):
        return (client[0], client[1], server[0], server[1], protocol)

    def _redis_key(self, key_tuple):
        return f"flow:{key_tuple[0]}:{key_tuple[1]}:{key_tuple[2]}:{key_tuple[3]}:{key_tuple[4]}"

    def update(self, flow, packet_size, sni=None, decision=None):
        client, server = self._identify_client_server(flow)
        key = self._make_key(client, server, flow["protocol"])
        is_new = key not in self.flows

        # Direction: kya ye packet client → server ja raha hai, ya server → client?
        is_client_to_server = (flow["src_ip"], flow["src_port"]) == client

        if is_new:
            self.flows[key] = {
                "client_ip": client[0],
                "client_port": client[1],
                "server_ip": server[0],
                "server_port": server[1],
                "protocol": flow["protocol"],
                "ip_version": flow["ip_version"],
                "packets_sent": 0,       # client → server
                "packets_received": 0,   # server → client
                "bytes_sent": 0,
                "bytes_received": 0,
                "sni": None,
                "decision": None,
                "start_time": time.time(),
            }

        entry = self.flows[key]

        if is_client_to_server:
            entry["packets_sent"] += 1
            entry["bytes_sent"] += packet_size
        else:
            entry["packets_received"] += 1
            entry["bytes_received"] += packet_size

        if sni and not entry["sni"]:
            entry["sni"] = sni

        if decision:
            entry["decision"] = decision

        redis_key = self._redis_key(key)
        redis_client.set(redis_key, json.dumps(entry), ex=3600)

        redis_client.incr("stats:total_packets")
        redis_client.incrby("stats:total_bytes", packet_size)

        return is_new, entry