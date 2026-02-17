#!/usr/bin/env python3
import os
import socket
import struct
import sys
import time
import zlib

SERVER_ADDRESS = "10.0.0.2"
SERVER_PORT = 5009

# MTU=1500 (IPv4): max UDP payload=1472
# Header here is 1(type)+4(seq)+2(len)+4(crc)=11 bytes => max data=1461
CHUNK_SIZE = 1461

# Sliding window settings
WINDOW_PKTS = 2048            # packets in flight (tune: 512..8192)
RETX_TIMEOUT = 0.01           # seconds before considering a packet "lost" (tune)
PACER_BURST = 400             # send this many packets then tiny sleep
PACER_SLEEP = 0.0002          # seconds (tune)
MAX_EOF_RETRIES = 200

# Packet types
TYPE_DATA = 0
TYPE_EOF  = 1

# Data header
HDR_FMT = "!BIHI"  # type(1) seq(4) len(2) crc32(4)
HDR_SIZE = struct.calcsize(HDR_FMT)

# ACK format:
# b'A' + ack_base(u32) + sack_len(u16) + sack_bytes
# sack bit i corresponds to (ack_base + 1 + i)
ACK_HDR_FMT = "!cIH"
ACK_HDR_SIZE = struct.calcsize(ACK_HDR_FMT)

# Final checksum format:
# b'F' + crc32(u32)
FILECRC_FMT = "!cI"
FILECRC_SIZE = struct.calcsize(FILECRC_FMT)


def compute_file_crc32(path: str) -> int:
    c = 0
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            c = zlib.crc32(b, c) & 0xFFFFFFFF
    return c


def parse_ack(pkt: bytes):
    """Returns (ack_base:int, sack:bytes) or None."""
    if len(pkt) < ACK_HDR_SIZE:
        return None
    tag, ack_base, sack_len = struct.unpack(ACK_HDR_FMT, pkt[:ACK_HDR_SIZE])
    if tag != b"A":
        return None
    sack = pkt[ACK_HDR_SIZE:ACK_HDR_SIZE + sack_len]
    if len(sack) != sack_len:
        return None
    return ack_base, sack


def parse_filecrc(pkt: bytes):
    if len(pkt) < FILECRC_SIZE:
        return None
    tag, crc = struct.unpack(FILECRC_FMT, pkt[:FILECRC_SIZE])
    if tag != b"F":
        return None
    return crc


def main():
    if len(sys.argv) < 2:
        print("Usage: udp_send_sw.py <file>")
        sys.exit(1)

    filename = sys.argv[1]
    filesize = os.path.getsize(filename)
    file_crc = compute_file_crc32(filename)

    print(f"Sending: {filename} ({filesize} bytes)")
    print(f"Local file CRC32: 0x{file_crc:08X}")

    # Precompute total packets
    total_pkts = (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE

    # Open socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.002)  # non-blocking-ish loop

        # Big send buffer
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32 * 1024 * 1024)

        server = (SERVER_ADDRESS, SERVER_PORT)

        # State
        base = 0                 # lowest unacked packet seq
        next_seq = 0             # next seq to send (0..total_pkts-1)
        acked = set()            # acked seqs in current window (small set)
        sent_time = {}           # seq -> last send timestamp
        cache = {}               # seq -> packet bytes (only for window)
        burst_counter = 0

        start = time.time()
        last_report = start

        # File handle for reading chunks
        with open(filename, "rb") as f:
            while base < total_pkts:
                # 1) Fill window with new packets
                while next_seq < total_pkts and (next_seq - base) < WINDOW_PKTS:
                    f.seek(next_seq * CHUNK_SIZE)
                    payload = f.read(CHUNK_SIZE)
                    crc = zlib.crc32(payload) & 0xFFFFFFFF
                    header = struct.pack(HDR_FMT, TYPE_DATA, next_seq, len(payload), crc)
                    pkt = header + payload

                    sock.sendto(pkt, server)
                    now = time.time()
                    sent_time[next_seq] = now
                    cache[next_seq] = pkt

                    next_seq += 1
                    burst_counter += 1
                    if burst_counter % PACER_BURST == 0:
                        time.sleep(PACER_SLEEP)

                # 2) Receive ACKs (as many as available quickly)
                while True:
                    try:
                        data, _ = sock.recvfrom(65535)
                    except socket.timeout:
                        break

                    # File CRC response (late) - ignore here
                    if data[:1] == b"F":
                        continue

                    parsed = parse_ack(data)
                    if not parsed:
                        continue
                    ack_base, sack = parsed

                    # Mark everything <= ack_base as acked
                    if ack_base >= base:
                        for s in range(base, min(ack_base + 1, total_pkts)):
                            acked.add(s)

                    # Mark SACK bits
                    # sack bit i => (ack_base + 1 + i)
                    for i, byte in enumerate(sack):
                        if byte == 0:
                            continue
                        for bit in range(8):
                            if byte & (1 << bit):
                                s = ack_base + 1 + i * 8 + bit
                                if 0 <= s < total_pkts:
                                    acked.add(s)

                    # Advance base while contiguous acked
                    while base in acked:
                        acked.remove(base)
                        sent_time.pop(base, None)
                        cache.pop(base, None)
                        base += 1

                # 3) Retransmit timed-out packets in window (selective)
                now = time.time()
                # Only scan the current window range
                scan_end = min(next_seq, base + WINDOW_PKTS)
                for s in range(base, scan_end):
                    if s in acked:
                        continue
                    t0 = sent_time.get(s)
                    if t0 is None:
                        continue
                    if (now - t0) >= RETX_TIMEOUT:
                        pkt = cache.get(s)
                        if pkt is not None:
                            sock.sendto(pkt, server)
                            sent_time[s] = now
                            burst_counter += 1
                            if burst_counter % PACER_BURST == 0:
                                time.sleep(PACER_SLEEP)

                # 4) Progress report
                if (now - last_report) > 0.5:
                    done = base
                    pct = (done / total_pkts) * 100 if total_pkts else 100
                    elapsed = now - start
                    sent_bits = min(done * CHUNK_SIZE, filesize) * 8
                    rate_mbps = (sent_bits / elapsed) / 1e6 if elapsed > 0 else 0
                    print(f"Progress: {done}/{total_pkts} ({pct:.1f}%)  est_rate={rate_mbps:.1f} Mb/s", end="\r")
                    last_report = now

        print("\nAll data packets ACKed.")

        # Send EOF and wait for file CRC reply
        eof_header = struct.pack(HDR_FMT, TYPE_EOF, total_pkts, 0, 0)
        retries = 0
        sock.settimeout(0.05)

        while True:
            sock.sendto(eof_header, server)
            try:
                data, _ = sock.recvfrom(1024)
            except socket.timeout:
                retries += 1
                if retries > MAX_EOF_RETRIES:
                    raise RuntimeError("Too many retries waiting for final checksum.")
                continue

            remote_crc = parse_filecrc(data)
            if remote_crc is None:
                continue

            print(f"Server file CRC32: 0x{remote_crc:08X}")
            if remote_crc == file_crc:
                print("End-to-end checksum MATCH.")
            else:
                print("Checksum MISMATCH.")
            break

        elapsed = time.time() - start
        mbps = (filesize * 8 / elapsed) / 1e6 if elapsed > 0 else 0
        print(f"Elapsed: {elapsed:.3f}s  Avg rate: {mbps:.2f} Mb/s")


if __name__ == "__main__":
    main()

