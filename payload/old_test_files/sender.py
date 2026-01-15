#!/usr/bin/env python3
import socket
import argparse
import time
import statistics

def udp_sender(target_ip, port, frames, frame_size, src_ip=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8*1024*1024)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8*1024*1024)

    if src_ip:
        sock.bind((src_ip, 0))

    print(f"[TX] Target {target_ip}:{port} frames={frames} size={frame_size} bytes")

    payload = b"A" * frame_size
    timestamps = {}
    sent_bytes = 0
    count = 0

    start_send = time.time()
    last_report = start_send
    last_bytes = 0

    for i in range(frames):
        message = f"{i}".encode()
        sock.sendto(message, (target_ip, port))
        timestamps[i] = time.time()
        sent_bytes += len(message)
        count += 1

        # Live TX rate reporting every 1s
        now = time.time()
        if now - last_report >= 1.0:
            interval_bytes = sent_bytes - last_bytes
            tx_rate = (interval_bytes * 8) / (now - last_report) / 1e6
            print(f"[TX] Sent {count}/{frames} packets | Current Tx rate: {tx_rate:.2f} Mbps")
            last_report = now
            last_bytes = sent_bytes

    end_send = time.time()
    send_time = end_send - start_send
    print(f"[TX] Finished sending {frames} packets in {send_time:.3f}s, waiting 2s for echoes...")

    # Wait for echoes
    sock.settimeout(2)
    received = 0
    latencies = []
    recv_bytes = 0
    start_recv = time.time()

    while True:
        try:
            data, _ = sock.recvfrom(2048)
            recv_time = time.time()
            if len(data) >= 1:  # accept even short echoes
                fid = int(data.decode(errors="ignore")) if data.decode(errors="ignore").isdigit() else -1
                if fid in timestamps:
                    latencies.append((recv_time - timestamps[fid]) * 1000)  # ms
                    received += 1
                    recv_bytes += len(data)
        except socket.timeout:
            break

    end_recv = time.time()
    recv_time = end_recv - start_recv

    # Compute final metrics
    loss = (frames - received) / frames * 100
    avg_latency = statistics.mean(latencies) if latencies else 0
    jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0
    tx_rate = (sent_bytes * 8) / send_time / 1e6
    rx_rate = (recv_bytes * 8) / recv_time / 1e6 if recv_time > 0 else 0

    print("\n--- Test Summary ---")
    print(f"Sent packets:         {frames}")
    print(f"Received echoes:      {received}")
    print(f"Lost packets:         {frames - received} ({loss:.2f}%)")
    print(f"Measured Tx rate:     {tx_rate:.2f} Mbps")
    print(f"Measured Rx rate:     {rx_rate:.2f} Mbps")
    print(f"Latency (ms):         avg={avg_latency:.3f}")
    print(f"Jitter (std dev ms):  {jitter:.3f}")
    print(f"Total send time:      {send_time:.3f} s")
    print(f"Total recv window:    {recv_time:.3f} s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Fiber Sender with Metrics")
    parser.add_argument("--target", type=str, default="10.0.0.1", help="Receiver IP")
    parser.add_argument("--port", type=int, default=5005, help="UDP port")
    parser.add_argument("--frames", type=int, default=10000, help="Number of packets to send")
    parser.add_argument("--frame_size", type=int, default=512, help="Packet payload size in bytes")
    parser.add_argument("--src_ip", type=str, default=None, help="Local source IP (optional)")
    args = parser.parse_args()

    udp_sender(args.target, args.port, args.frames, args.frame_size, args.src_ip)

