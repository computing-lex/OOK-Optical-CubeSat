import socket
import time
import argparse

def udp_receiver(listen_ip, port, timeout, rx_power):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))
    sock.settimeout(timeout)

    print(f"--- UDP Fiber Receiver ---")
    print(f"Listening on {listen_ip}:{port}")
    print(f"Rx Optical Power (simulated): {rx_power} dBm\n")

    total_bytes = 0
    packets = 0
    start_time = time.time()

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            total_bytes += len(data)
            packets += 1

            # Echo back for latency/jitter calculation
            sock.sendto(data, addr)
    except socket.timeout:
        pass

    elapsed = time.time() - start_time
    if packets > 0:
        data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
        print(f"\n--- Receiver Summary ---")
        print(f"Packets Received: {packets}")
        print(f"Total Bytes: {total_bytes}")
        print(f"Elapsed Time: {elapsed:.2f} s")
        print(f"Measured Rx Data Rate: {data_rate_mbps:.2f} Mbps")
    else:
        print("No packets received.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Fiber Receiver with Rx Power and Echo Response")
    parser.add_argument("--listen", type=str, default="10.0.0.1", help="Local IP to listen on")
    parser.add_argument("--port", type=int, default=5005, help="UDP port")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    parser.add_argument("--rx_power", type=float, default=-3.0, help="Rx optical power (dBm, simulated)")
    args = parser.parse_args()

    udp_receiver(args.listen, args.port, args.timeout, args.rx_power)

