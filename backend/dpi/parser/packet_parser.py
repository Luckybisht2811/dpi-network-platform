from scapy.all import IP, IPv6, TCP, UDP, Raw

DEBUG_SNI = False


def extract_five_tuple(packet):
    if packet.haslayer(IP):
        ip_layer = packet[IP]
        ip_version = 4
    elif packet.haslayer(IPv6):
        ip_layer = packet[IPv6]
        ip_version = 6
    else:
        return None

    protocol = None
    src_port = None
    dst_port = None

    if packet.haslayer(TCP):
        protocol = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif packet.haslayer(UDP):
        protocol = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
    else:
        return None

    return {
        "src_ip": ip_layer.src,
        "dst_ip": ip_layer.dst,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "ip_version": ip_version,
    }


def extract_sni_from_bytes(data: bytes):
    """
    Core SNI parsing logic — raw TCP payload bytes leta hai.
    Scapy aur pydivert dono yahi function use karenge.
    """
    try:
        if len(data) < 6:
            return None
        if data[0] != 0x16:          # TLS Handshake record
            return None
        if data[5] != 0x01:          # ClientHello
            return None

        pos = 5 + 4
        pos += 2 + 32                # Version + Random

        session_id_len = data[pos]
        pos += 1 + session_id_len

        cipher_len = int.from_bytes(data[pos:pos+2], "big")
        pos += 2 + cipher_len

        comp_len = data[pos]
        pos += 1 + comp_len

        if pos + 2 > len(data):
            return None

        ext_total_len = int.from_bytes(data[pos:pos+2], "big")
        pos += 2
        ext_end = pos + ext_total_len

        while pos + 4 <= ext_end and pos + 4 <= len(data):
            ext_type = int.from_bytes(data[pos:pos+2], "big")
            ext_len = int.from_bytes(data[pos+2:pos+4], "big")
            ext_data_start = pos + 4

            if ext_type == 0x0000:
                sni_list_start = ext_data_start + 2
                name_len = int.from_bytes(data[sni_list_start+1:sni_list_start+3], "big")
                name_start = sni_list_start + 3
                return data[name_start:name_start+name_len].decode("utf-8", errors="ignore")

            pos = ext_data_start + ext_len

        return None

    except (IndexError, UnicodeDecodeError):
        return None


def extract_sni(packet):
    """Scapy packet se SNI nikalne ka wrapper."""
    if not packet.haslayer(Raw):
        return None
    return extract_sni_from_bytes(bytes(packet[Raw].load))