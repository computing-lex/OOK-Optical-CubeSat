import socket
import time
import subprocess
import re
import argparse

def get_optical_power(interface="enP7p1s0f0"):
    """Reads TX optical power (dBm) from SFP using ethtool."""
    try:
        result = subprocess.check_output(["sudo", "ethtool", "-m", interface], text=True)
        tx_match = re.search(r"Laser output power:\s+([-+]?\d*\.\d+|\d+)", result)
        tx_power = float(tx_match.group(1)) if tx_match else None
        return tx_power
    except subprocess.CalledProcessError:
        return None

def udp_sender(target_ip, port, duration, payload_size, interface):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b"x" * payload_size

    print(f"Sending to {target_ip}:{port} for {duration} seconds...")
    start_time = time.time()
    packets = 0
    total_bytes = 0

    while time.time() - start_time < duration:
        sock.sendto(payload, (target_ip, port))
        packets += 1
        total_bytes += len(payload)

    elapsed = time.time() - start_time
    data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
    data_rate_MBps = data_rate_mbps / 8

    tx_power = get_optical_power(interface)

    print(f"\n=== UDP TRANSMIT STATS ===")
    print(f"Packets sent        : {packets}")
    print(f"Bytes sent          : {total_bytes}")
    print(f"Elapsed time (s)    : {elapsed:.2f}")
    print(f"Transmit rate       : {data_rate_MBps:.2f} MB/s")

    if tx_power is not None:
        print(f"TX optical power    : {tx_power:.2f} dBm")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Sender with Optical Power Diagnostics")
    parser.add_argument("--target", default="10.0.0.1", help="Target IP address (default: 10.0.0.1)")
    parser.add_argument("--port", type=int, default=5005, help="Target port (default: 5005)")
    parser.add_argument("--duration", type=int, default=5, help="Send duration in seconds (default: 5)")
    parser.add_argument("--payload", type=int, default=1472, help="UDP payload size in bytes (default: 1472)")
    parser.add_argument("--interface", default="enP7p1s0f0", help="Network interface for SFP diagnostics")
    args = parser.parse_args()

    udp_sender(args.target, args.port, args.duration, args.payload, args.interface)

