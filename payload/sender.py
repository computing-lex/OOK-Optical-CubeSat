import socket
import time
import argparse
import statistics

def udp_sender(target_ip, port, frames, tx_power, frame_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    print(f"--- UDP Fiber Sender ---")
    print(f"Target: {target_ip}:{port}")
    print(f"Frames: {frames}, Frame Size: {frame_size} bytes")
    print(f"Tx Optical Power (simulated): {tx_power} dBm\n")

    total_bytes = 0
    lost_packets = 0
    latency_samples = []
    start_time = time.time()

    for seq in range(frames):
        tx_timestamp = time.time()
        header = f"{seq},{tx_timestamp}".encode().ljust(32, b' ')
        payload = header + b"x" * (frame_size - len(header))

        try:
            sock.sendto(payload, (target_ip, port))
            total_bytes += len(payload)

            data, _ = sock.recvfrom(2048)
            rx_timestamp = time.time()

            _, tx_timestamp_recv = data[:8].decode(errors="ignore").split(',')
            rtt_ms = (rx_timestamp - float(tx_timestamp_recv)) * 1000
            latency_samples.append(rtt_ms)
        except Exception:
            lost_packets += 1

        if (seq + 1) % 1000 == 0:
            print(f"Sent frame {seq + 1}/{frames}")

    elapsed = time.time() - start_time
    sent_packets = frames
    received_packets = frames - lost_packets

    # Performance metrics
    data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
    packet_loss = (lost_packets / sent_packets) * 100 if sent_packets else 0
    avg_latency = statistics.mean(latency_samples) if latency_samples else 0
    jitter = statistics.stdev(latency_samples) if len(latency_samples) > 1 else 0

    print(f"\n--- Transmission Summary ---")
    print(f"Sent: {sent_packets}, Received Echo: {received_packets}")
    print(f"Packet Loss: {packet_loss:.2f}%")
    print(f"Average Latency: {avg_latency:.3f} ms")
    print(f"Jitter: {jitter:.3f} ms")
    print(f"Measured Data Rate: {data_rate_mbps:.2f} Mbps")
    print(f"Total Transfer Time: {elapsed:.3f} s")
    print(f"Tx Optical Power (simulated): {tx_power} dBm")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Fiber Sender with Latency, Jitter, and Packet Loss Measurement")
    parser.add_argument("--target", type=str, default="10.0.0.1", help="Receiver IP address")
    parser.add_argument("--port", type=int, default=5005, help="UDP port")
    parser.add_argument("--frames", type=int, default=10000, help="Number of frames to send")
    parser.add_argument("--frame_size", type=int, default=512, help="Frame size in bytes")
    parser.add_argument("--tx_power", type=float, default=-2.5, help="Tx optical power (dBm, simulated)")
    args = parser.parse_args()

    udp_sender(args.target, args.port, args.frames, args.tx_power, args.frame_size)

