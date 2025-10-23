#!/usr/bin/env python3
# fiber_speed_test_sender.py
import socket
import time
import argparse
import threading
import struct
import statistics

HEADER_FMT = "!Id"   # network byte order: unsigned int (4) + double (8) => 12 bytes
HEADER_LEN = struct.calcsize(HEADER_FMT)

def receiver_thread(sock, frames, recv_dict, latencies, stop_event):
    """Thread that receives echoes and records RTTs by matching seq -> tx_time"""
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(65536)
        except socket.timeout:
            continue
        now = time.time()
        if len(data) < HEADER_LEN:
            continue
        try:
            seq, tx_ts = struct.unpack(HEADER_FMT, data[:HEADER_LEN])
        except struct.error:
            continue
        # compute RTT (ms)
        rtt_ms = (now - tx_ts) * 1000.0
        latencies.append(rtt_ms)
        # mark as received
        recv_dict[seq] = now

def udp_sender(target_ip, port, frames, frame_size, src_ip=None):
    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    # increase buffers for higher throughput
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)

    if src_ip:
        sock.bind((src_ip, 0))

    print(f"[TX] Target {target_ip}:{port} frames={frames} size={frame_size} bytes")

    # shared structures
    recv_dict = {}            # seq -> receive_time (presence means echoed back)
    latencies = []            # list of RTT ms
    stop_event = threading.Event()

    # start receiver thread (listens for echoes)
    recv_t = threading.Thread(target=receiver_thread, args=(sock, frames, recv_dict, latencies, stop_event), daemon=True)
    recv_t.start()

    # build payload buffer
    total_bytes = 0
    start_time = time.time()

    for seq in range(frames):
        tx_ts = time.time()
        header = struct.pack(HEADER_FMT, seq, tx_ts)
        if frame_size < HEADER_LEN:
            raise ValueError(f"frame_size must be >= {HEADER_LEN}")
        payload = header + b"\x55" * (frame_size - HEADER_LEN)
        try:
            sock.sendto(payload, (target_ip, port))
            total_bytes += len(payload)
        except Exception as e:
            print(f"[TX] send error seq={seq}: {e}")
        # no per-packet recv blocking — fire-and-forget
        # optionally throttle here if you want lower sender rate

        # small yield to avoid starving receiver thread on some systems
        if seq % 10000 == 0 and seq != 0:
            time.sleep(0.0001)

    # sending done — give receiver some time to collect echoes
    send_elapsed = time.time() - start_time
    grace = 2.0
    print(f"[TX] Finished sending {frames} packets in {send_elapsed:.3f}s, waiting {grace}s for echoes...")
    time.sleep(grace)
    stop_event.set()
    recv_t.join(timeout=1.0)

    # compute metrics
    sent_packets = frames
    received_packets = len(recv_dict)
    lost_packets = sent_packets - received_packets
    packet_loss_pct = (lost_packets / sent_packets) * 100.0 if sent_packets else 0.0
    data_rate_mbps = (total_bytes * 8) / (send_elapsed * 1_000_000) if send_elapsed > 0 else 0.0
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    min_latency = min(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    print("\n--- Test Summary ---")
    print(f"Sent packets:         {sent_packets}")
    print(f"Received echoes:      {received_packets}")
    print(f"Lost packets:         {lost_packets} ({packet_loss_pct:.2f}%)")
    print(f"Measured Tx rate:     {data_rate_mbps:.2f} Mbps (based on send time)")
    print(f"Latency (ms): avg={avg_latency:.3f} min={min_latency:.3f} max={max_latency:.3f}")
    print(f"Jitter (std dev ms):  {jitter:.3f}")
    print(f"Total send time:      {send_elapsed:.3f} s")
    print(f"Note: Small grace window was used to collect echoes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="10.0.0.1", help="Receiver IP")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--frames", type=int, default=10000)
    parser.add_argument("--frame_size", type=int, default=512)
    parser.add_argument("--src_ip", default=None, help="Source IP to bind (optional)")
    args = parser.parse_args()

    udp_sender(args.target, args.port, args.frames, args.frame_size, args.src_ip)

