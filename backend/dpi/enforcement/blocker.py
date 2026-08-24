import time
import json
import pydivert
from pydivert import Packet
from dpi.policies.blocklist import is_blocked
from dpi.parser.packet_parser import extract_sni_from_bytes
from app.core.redis import redis_client

blocked_flows = set()
allowed_flows = set()
handshake_buffers = {}
stats = {"allowed": 0, "blocked": 0, "dropped_packets": 0, "quic_blocked": 0}

MAX_BUFFER_SIZE = 16384
LIVE_TTL_SECONDS = 60  # kitni der tak domain "active" dikhega dashboard par


def make_flow_key(src_ip, src_port, dst_ip, dst_port):
    if dst_port == 443:
        return (src_ip, src_port, dst_ip, dst_port)
    else:
        return (dst_ip, dst_port, src_ip, src_port)


def log_live_allowed(sni, client_ip):
    """Har allowed connection ko ek 'live' sorted set me daalta hai — dashboard isko
    poll karke dikhata hai 'abhi kya chal raha hai'. Score = timestamp, isliye
    purane entries automatically 'expire' ho jate hain (window ke bahar filter ho jate hain)."""
    try:
        redis_client.zadd("live:allowed", {sni: time.time()})
        redis_client.incr("stats:total_allowed")
    except Exception as e:
        print(f"[WARN] Live-allowed logging failed: {e}")


def log_blocked_event(sni, client_ip, client_port, server_ip, server_port):
    event = {
        "sni": sni,
        "client_ip": client_ip,
        "client_port": client_port,
        "server_ip": server_ip,
        "server_port": server_port,
        "timestamp": time.time(),
    }
    redis_client.lpush("blocked_events", json.dumps(event))
    redis_client.ltrim("blocked_events", 0, 499)
    redis_client.incr("stats:total_blocked")
    redis_client.hincrby("stats:blocked_by_domain", sni, 1)
    redis_client.hincrby("stats:blocked_by_client", client_ip, 1)

    # Live "abhi block ho raha hai" set ke liye
    redis_client.zadd("live:blocked", {sni: time.time()})


def send_rst(packet, w):
    rst = Packet(bytes(packet.raw), packet.interface, packet.direction)
    rst.tcp.rst = True
    rst.tcp.ack = True
    rst.tcp.syn = False
    rst.tcp.fin = False
    rst.src_addr, rst.dst_addr = packet.dst_addr, packet.src_addr
    rst.src_port, rst.dst_port = packet.dst_port, packet.src_port
    rst.recalculate_checksums()
    try:
        w.send(rst)
    except Exception:
        pass


def handle_packet(packet, w):
    if packet.udp and (packet.dst_port == 443 or packet.src_port == 443):
        stats["quic_blocked"] += 1
        return

    if not packet.tcp:
        w.send(packet)
        return

    key = make_flow_key(packet.src_addr, packet.src_port, packet.dst_addr, packet.dst_port)

    if key in blocked_flows:
        stats["dropped_packets"] += 1
        send_rst(packet, w)
        return

    if key in allowed_flows:
        w.send(packet)
        return

    payload = packet.tcp.payload
    if payload:
        existing = handshake_buffers.get(key, b"")
        combined = existing + bytes(payload)

        if len(combined) > MAX_BUFFER_SIZE:
            handshake_buffers.pop(key, None)
            w.send(packet)
            return

        sni = extract_sni_from_bytes(combined)

        if sni:
            handshake_buffers.pop(key, None)
            client_ip, client_port, server_ip, server_port = key

            if is_blocked(sni):
                blocked_flows.add(key)
                stats["blocked"] += 1
                print(f"🚫 BLOCKING NEW CONNECTION: {sni}  {key}")
                try:
                    log_blocked_event(sni, client_ip, client_port, server_ip, server_port)
                except Exception as e:
                    print(f"[WARN] Redis logging failed: {e}")
                send_rst(packet, w)
                return
            else:
                allowed_flows.add(key)
                stats["allowed"] += 1
                print(f"✅ ALLOWED: {sni}")
                log_live_allowed(sni, client_ip)
                w.send(packet)
                return
        else:
            if combined[:1] == b"\x16":
                handshake_buffers[key] = combined

    w.send(packet)


def start_blocking():
    win_filter = "tcp.DstPort == 443 or tcp.SrcPort == 443 or udp.DstPort == 443 or udp.SrcPort == 443"

    print("DPI Blocking Engine Started.")
    print(f"Filter: {win_filter}")
    print("Press Ctrl+C to stop...\n")

    with pydivert.WinDivert(win_filter) as w:
        try:
            for packet in w:
                try:
                    handle_packet(packet, w)
                except Exception as e:
                    print(f"[ERROR] {e} — fail-open, packet forward kar raha hoon")
                    w.send(packet)
        except KeyboardInterrupt:
            pass

    print(f"\nStats: {stats}")