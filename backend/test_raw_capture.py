from scapy.all import sniff

count = {"total": 0}

def show(pkt):
    count["total"] += 1
    print(f"[{count['total']}] {pkt.summary()}")

print("Capturing ALL traffic for 15 seconds on Wi-Fi...")
sniff(iface="Wi-Fi", prn=show, store=False, timeout=15)
print(f"\nTotal packets captured: {count['total']}")