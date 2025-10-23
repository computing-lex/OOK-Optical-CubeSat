import socket
import argparse
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind_ip", default="0.0.0.0", help="Receiver IP address")
    parser.add_argument("--port", type=int, default=5005, help="UDP port to listen on")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind_ip, args.port))
    sock.settimeout(5)

    print(f"[RX] Listening on {args.bind_ip}:{args.port} ...")

    total_bytes = 0
    received = 0
    start_time = time.time()

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            received += 1
            total_bytes += len(data)
            sock.sendto(data, addr)  # Echo back
        except socket.timeout:
            break

    end_time = time.time()
    elapsed = end_time - start_time
    rx_rate_mbps = (total_bytes * 8) / (elapsed * 1e6) if elapsed > 0 else 0

    print("\n--- Receiver Summary ---")
    print(f"Received packets:     {received}")
    print(f"Total bytes:          {total_bytes}")
    print(f"Elapsed time:         {elapsed:.3f} s")
    print(f"Measured Rx rate:     {rx_rate_mbps:.2f} Mbps")

    sock.close()

if __name__ == "__main__":
    main()

