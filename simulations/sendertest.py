#!/usr/bin/env python3
"""
UDP sender with:
 - configurable data rate (Mbps),
 - total frames,
 - packet size,
 - simulated transmitter error rate (TX_ERROR_RATE),
 - per-packet CRC32 for verification by receiver.

Usage:
    python3 sender.py --dest 127.0.0.1 --port 5005 --frames 50 --rate 100 --size 1472 --tx-error 0.0
"""
import socket
import time
import struct
import argparse
import zlib
import random

parser = argparse.ArgumentParser()
parser.add_argument("--dest", default="127.0.0.1", help="Destination IP")
parser.add_argument("--port", type=int, default=5005, help="Destination port")
parser.add_argument("--frames", type=int, default=50, help="Total frames to send")
parser.add_argument("--rate", type=float, default=100.0, help="Target data rate in Mbps")
parser.add_argument("--size", type=int, default=1472, help="Total packet size in bytes (including seq and CRC)")
parser.add_argument("--tx-error", type=float, default=0.0, help="Simulated TX error rate (0.0-1.0), probability to corrupt a packet before sending")
parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")

args = parser.parse_args()

DEST_IP = args.dest
DEST_PORT = args.port
TOTAL_FRAMES = args.frames
DATA_RATE_Mbps = args.rate
PACKET_SIZE = args.size
TX_ERROR_RATE = args.tx_error
SEED = args.seed

if PACKET_SIZE < 12:
    raise SystemExit("PACKET_SIZE must be at least 12 bytes (4 bytes seq + >=0 payload + 4 bytes CRC)")

if SEED is not None:
    random.seed(SEED)

# compute payload length: sequence (4 bytes) + payload + crc (4 bytes) = PACKET_SIZE
PAYLOAD_LEN = PACKET_SIZE - 8  # 4 for seq, 4 for crc

bytes_per_sec = (DATA_RATE_Mbps * 1_000_000) / 8.0  # bytes/sec
delay_per_packet = PACKET_SIZE / bytes_per_sec  # seconds per packet ideal

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)

print(f"Sender -> {DEST_IP}:{DEST_PORT}")
print(f"Packet size: {PACKET_SIZE} bytes (seq4 + payload{PAYLOAD_LEN} + crc4)")
print(f"Frames: {TOTAL_FRAMES}, Target rate: {DATA_RATE_Mbps} Mbps, TX error rate: {TX_ERROR_RATE}")
print(f"Delay per packet (ideal): {delay_per_packet:.6f} s")

total_sent_bytes = 0
start_time_all = time.time()
corrupted_sent = 0

for seq in range(1, TOTAL_FRAMES + 1):
    # build payload (seq + filler payload)
    seq_bytes = struct.pack("!I", seq)
    data_payload = bytes((seq % 256,) * PAYLOAD_LEN)  # deterministic filler for easier debugging
    crc = zlib.crc32(seq_bytes + data_payload) & 0xFFFFFFFF
    crc_bytes = struct.pack("!I", crc)
    packet = seq_bytes + data_payload + crc_bytes

    # Simulate transmitter corruption with probability TX_ERROR_RATE
    if TX_ERROR_RATE > 0.0 and random.random() < TX_ERROR_RATE:
        # flip a byte somewhere in the packet (not the CRC so corruption will be detected)
        idx = random.randrange(0, len(packet) - 4)  # avoid last 4 bytes (CRC) so CRC no longer matches
        # convert to bytearray to flip
        ba = bytearray(packet)
        ba[idx] ^= 0xFF  # flip bits
        packet = bytes(ba)
        corrupted_sent += 1

    t0 = time.time()
    sock.sendto(packet, (DEST_IP, DEST_PORT))
    total_sent_bytes += len(packet)
    send_elapsed = time.time() - t0

    # maintain data rate (sleep the remainder)
    to_sleep = delay_per_packet - send_elapsed
    if to_sleep > 0:
        time.sleep(to_sleep)

    print(f"Sent frame {seq:04d} {'(corrupted at TX)' if TX_ERROR_RATE>0 and corrupted_sent and seq<=corrupted_sent else ''}")

elapsed_all = time.time() - start_time_all
throughput_mbps_actual = (total_sent_bytes * 8) / (elapsed_all * 1_000_000)

print("\n--- Transmission Summary ---")
print(f"Frames attempted: {TOTAL_FRAMES}")
print(f"Total bytes sent: {total_sent_bytes}")
print(f"TX corrupted packets (sim): {corrupted_sent}")
print(f"Elapsed time: {elapsed_all:.3f} s")
print(f"Achieved throughput: {throughput_mbps_actual:.2f} Mbps")

sock.close()
