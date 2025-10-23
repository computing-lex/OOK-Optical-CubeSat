#!/usr/bin/env python3
import socket
import argparse
import time
import statistics

def udp_receiver(bind_ip, port, echo=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8*1024*1024)
    sock.bind((bind_ip, port))
    print(f"[RX] Listening on {bind_ip}:{port} (echo={'on' if echo else 'off'})")

    count = 0
    recv_bytes = 0
    start_time = time.time()
    latencies = []
    last_time = start_time
    last_recv_bytes = recv_bytes

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            print(f"Packet Received: {data.decode("utf-8")}")
            now = time.time()
            recv_bytes += len(data)
            last_recv_bytes += len(data)
            count += 1

            if echo:
                sock.sendto(data, addr)

            # Latency/jitter measure (RX side only — time between arrivals)
            latencies.append((now - last_time) * 1000)
            last_time = now

            if count % 1000 == 0:
                elapsed = now - start_time
                rate = (last_recv_bytes * 8) / elapsed / 1e6
                print(f"[RX] {count} packets received ({rate:.2f} Mbps avg)")
                last_recv_bytes = 0 # reset
    except KeyboardInterrupt:
        pass

    end_time = time.time()
    total_time = end_time - start_time
    rx_rate = (recv_bytes * 8) / total_time / 1e6
    jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0

    print("\n--- Receiver Summary ---")
    print(f"Total packets:     {count}")
    print(f"Total bytes:       {recv_bytes}")
    print(f"Average data rate: {rx_rate:.2f} Mbps")
    print(f"Jitter (ms):       {jitter:.3f}")
    print(f"Total time:        {total_time:.3f} s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Fiber Receiver with Metrics")
    parser.add_argument("--bind", type=str, default="10.0.0.1", help="Local bind IP")
    parser.add_argument("--port", type=int, default=5005, help="UDP port to listen on")
    parser.add_argument("--no-echo", action="store_true", help="Disable echo")
    args = parser.parse_args()

    udp_receiver(args.bind, args.port, not args.no_echo)

