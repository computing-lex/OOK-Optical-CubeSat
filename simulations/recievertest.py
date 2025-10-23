#!/usr/bin/env python3
"""
UDP receiver with:
 - CRC32 verification,
 - configurable packet size and total frames,
 - optional simulated receiver-side error injection (RX_ERROR_RATE),
 - reports frames lost, corrupted, throughput, and error stats.

Usage:
    python3 receiver.py --listen 0.0.0.0 --port 5005 --frames 50 --size 1472 --rx-error 0.0
"""
import socket
import struct
import time
import argparse
import zlib
import random

parser = argparse.ArgumentParser()
parser.add_argument("--listen", default="0.0.0.0", help="Listen IP")
parser.add_argument("--port", type=int, default=5005, help="Listen port")
parser.add_argument("--frames", type=int, default=50, help="Total frames expected")
parser.add_argument("--size", type=int, default=1472, help="Expected packet size in bytes (including seq and CRC)")
parser.add_argument("--rx-error", type=float, default=0.0, help="Simulated RX error rate (0.0-1.0), probability to corrupt received data before CRC check")
parser.add_argument("--timeout", type=float, default=5.0, help="Socket timeout in seconds to stop after inactivity")
parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
args = parser.parse_args()

LISTEN_IP = args.listen
LISTEN_PORT = args.port
TOTAL_FRAMES = args.frames
PACKET_SIZE = args.size
RX_ERROR_RATE = args.rx_error
TIMEOUT = args.timeout
SEED = args.seed

if PACKET_SIZE < 12:
    raise SystemExit("PACKET_SIZE must be at least 12 bytes (4 bytes seq + >=0 payload + 4 bytes CRC)")

if SEED is not None:
    random.seed(SEED)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
sock.settimeout(TIMEOUT)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)

print(f"Listening for UDP packets on {LISTEN_IP}:{LISTEN_PORT}")
print(f"Expecting {TOTAL_FRAMES} frames of size {PACKET_SIZE} bytes. RX error rate (sim): {RX_ERROR_RATE}")
received_frames = set()
corrupted_frames = 0
total_bytes = 0
start_time = None
received_count = 0

while len(received_frames) < TOTAL_FRAMES:
    try:
        data, addr = sock.recvfrom(65536)
        if start_time is None:
            start_time = time.time()
        recv_len = len(data)
        total_bytes += recv_len
        received_count += 1

        # If a sender uses the same PACKET_SIZE convention, the data layout is:
        # 4 bytes seq | payload (PAYLOAD_LEN) | 4 bytes crc
        if recv_len < 8:
            print(f"Received tiny packet of {recv_len} bytes from {addr}, ignoring")
            continue

        # Simulate receiver-side corruption BEFORE CRC check if requested
        if RX_ERROR_RATE > 0.0 and random.random() < RX_ERROR_RATE:
            # flip a byte (not CRC) to force CRC mismatch
            mutable = bytearray(data)
            if len(mutable) > 8:
                idx = random.randrange(0, len(mutable) - 4)
                mutable[idx] ^= 0xFF
                data = bytes(mutable)

        seq_num = struct.unpack('!I', data[:4])[0]
        crc_recv = struct.unpack('!I', data[-4:])[0]
        payload = data[: -4]  # everything up to CRC
        crc_calc = zlib.crc32(payload) & 0xFFFFFFFF

        if crc_recv != crc_calc:
            corrupted_frames += 1
            print(f"Frame {seq_num:04d} received from {addr} -- CRC MISMATCH (recv:{crc_recv:#010x} calc:{crc_calc:#010x})")
        else:
            print(f"Received frame {seq_num:04d} from {addr} (ok)")

        received_frames.add(seq_num)

    except socket.timeout:
        print("Socket timeout / inactivity reached, stopping receive.")
        break
    except KeyboardInterrupt:
        print("Interrupted by user.")
        break

elapsed = (time.time() - start_time) if start_time else 0.0001
missing = set(range(1, TOTAL_FRAMES + 1)) - received_frames
errors = len(missing) + corrupted_frames
throughput_mbps = (total_bytes * 8) / (elapsed * 1_000_000)

print("\n--- Reception Summary ---")
print(f"Total frames expected: {TOTAL_FRAMES}")
print(f"Total frames received (distinct seq): {len(received_frames)}")
print(f"Packets received (including duplicates): {received_count}")
print(f"Frames corrupted (CRC mismatch): {corrupted_frames}")
print(f"Frames missing (not received): {len(missing)}")
print(f"Total errors (missing + corrupted): {errors}")
print(f"Estimated throughput: {throughput_mbps:.2f} Mbps")
print(f"Elapsed time: {elapsed:.3f} seconds")
print(f"Missing frame list (first 20 shown): {sorted(list(missing))[:20]}")

sock.close()
