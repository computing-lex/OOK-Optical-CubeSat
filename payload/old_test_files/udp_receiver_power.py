import socket
import time
import subprocess
import re
import argparse

def get_optical_power(interface="enP7p1s0f0"):
    """Reads TX and RX optical power from SFP using ethtool, ignoring errors."""
    try:
        result = subprocess.check_output(
            ["sudo", "ethtool", "-m", interface],
            text=True,
            stderr=subprocess.DEVNULL  # hide netlink error
        )
        tx_match = re.search(r"Laser output power:\s+([-+]?\d*\.\d+|\d+)", result)
        rx_match = re.search(r"Receiver signal average optical power:\s+([-+]?\d*\.\d+|\d+)", result)
        tx_power = float(tx_match.group(1)) if tx_match else None
        rx_power = float(rx_match.group(1)) if rx_match else None
        return tx_power, rx_power
    except subprocess.CalledProcessError:
        return None, None

def udp_receiver(listen_ip, port, timeout, interface):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))
    sock.settimeout(timeout)

    print(f"Listening on {listen_ip}:{port} for up to {timeout} seconds...")
    total_bytes = 0
    packets = 0
    start_time = None  # Timer starts when first packet arrives

    try:
        while True:
            data, _ = sock.recvfrom(65535)
            if start_time is None:
                start_time = time.time()
            total_bytes += len(data)
            packets += 1
    except socket.timeout:
        pass

    if packets > 0:
        elapsed = time.time() - start_time
        data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
        data_rate_MBps = data_rate_mbps / 8

        tx_power, rx_power = get_optical_power(interface)

        print(f"\n=== UDP RECEIVE STATS ===")
        print(f"Frames received     : {packets}")
        print(f"Total bytes         : {total_bytes}")
        print(f"Elapsed time (s)    : {elapsed:.2f}")
        print(f"Receive rate        : {data_rate_MBps:.2f} MB/s")

        if tx_power is not None and rx_power is not None:
            print(f"TX optical power    : {tx_power:.2f} dBm")
            print(f"RX optical power    : {rx_power:.2f} dBm")

            if rx_power > -1 or rx_power < -25:
                print("RX optical power outside nominal range (-1 to -25 dBm)")
        else:
            print("Optical power info  : Not available (no SFP diagnostics)")
    else:
        print("No data received (no packets arrived before timeout).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver with Optical Power Diagnostics")
    parser.add_argument("--ip", default="10.0.0.1", help="Listening IP address (default: 10.0.0.1)")
    parser.add_argument("--port", type=int, default=5005, help="Listening port (default: 5005)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout duration in seconds (default: 5)")
    parser.add_argument("--interface", default="enP7p1s0f0", help="Network interface for SFP diagnostics")
    args = parser.parse_args()

    udp_receiver(args.ip, args.port, args.timeout, args.interface)

