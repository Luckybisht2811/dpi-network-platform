from dpi.capture.sniffer import start_capture

if __name__ == "__main__":
    start_capture(
        interface="Wi-Fi",
        packet_count=0,
        bpf_filter="tcp port 443",
        timeout=25,
    )