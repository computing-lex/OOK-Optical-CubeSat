import socket
import time
import argparse
import statistics

def tcp_sender(target_ip, port, frame_size, frames, echo=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((target_ip, port))

    payload = b'A' * frame_size
    send_times, recv_times = [], []

    print(f"[TX] Connected to {target_ip}:{port}")
    print(f"[TX] Frame size={frame_size}B, frames={frames}, echo={echo}")

    start_send = time.perf_counter()

    for _ in range(frames):
        t0 = time.perf_counter()
        sock.sendall(payload)
        send_times.append(t0)
        if echo:
            data = sock.recv(frame_size)
            recv_times.append(time.perf_counter())

    end_send = time.perf_counter()
    send_duration = end_send - start_send

    # If echo is enabled, compute round-trip latency
    if echo and recv_times:
        latencies = [(r - s) * 1000 for s, r in zip(send_times, recv_times)]
        avg_latency = statistics.mean(latencies)
        jitter = statistics.pstdev(latencies)
    else:
        avg_latency = jitter = 0

    total_bytes = frame_size * frames
    tx_rate = (total_bytes * 8) / (send_duration * 1e6)

    print("\n--- Sender Summary ---")
    print(f"Total sent data:      {total_bytes / 1e6:.2f} MB")
    print(f"Total send time:      {send_duration:.3f} s")
    print(f"Measured Tx rate:     {tx_rate:.2f} Mbps")
    if echo:
        print(f"Latency (ms):         avg={avg_latency:.3f}")
        print(f"Jitter (std dev ms):  {jitter:.3f}")

    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Sender")
    parser.add_argument("--target", required=True, help="Receiver IP address")
    parser.add_argument("--port", type=int, default=5005, help="Destination TCP port")
    parser.add_argument("--frame_size", type=int, default=1024, help="Payload size in bytes")
    parser.add_argument("--frames", type=int, default=10000, help="Number of frames to send")
    parser.add_argument("--echo", action="store_true", help="Expect echo for latency test")
    args = parser.parse_args()

    tcp_sender(args.target, args.port, args.frame_size, args.frames, args.echo)

