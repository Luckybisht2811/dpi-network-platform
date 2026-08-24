from scapy.all import sniff, Raw
from dpi.parser.packet_parser import extract_five_tuple, extract_sni
from dpi.flows.flow_tracker import FlowTracker
from dpi.policies.policy_engine import PolicyEngine

tracker = FlowTracker()
policy = PolicyEngine()


def process_packet(packet):
    flow = extract_five_tuple(packet)
    if not flow:
        return

    packet_size = len(packet)
    sni = None
    decision = None

    if packet.haslayer(Raw):
        sni = extract_sni(packet)

    if sni:
        decision = policy.evaluate(sni, flow)

    is_new, entry = tracker.update(flow, packet_size, sni, decision)

    if is_new:
        print(f"[NEW FLOW] {flow['src_ip']}:{flow['src_port']} → "
              f"{flow['dst_ip']}:{flow['dst_port']} ({flow['protocol']})")

    if sni:
        if decision == "BLOCK":
            print(f"    🚫 BLOCKED: {sni}")
        else:
            print(f"    ✅ ALLOWED: {sni}")


def start_capture(interface: str, packet_count: int = 0, bpf_filter: str = None, timeout: int = None):
    print(f"Starting capture on interface: {interface}")
    if bpf_filter:
        print(f"Filter: {bpf_filter}")
    print("Press Ctrl+C to stop...\n")

    sniff(
        iface=interface,
        prn=process_packet,
        store=False,
        count=packet_count,
        filter=bpf_filter,
        timeout=timeout,
    )

    print(f"\nTotal unique flows tracked: {len(tracker.flows)}")
    print(f"Policy stats: {policy.stats()}")