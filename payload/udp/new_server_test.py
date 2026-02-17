#!/usr/bin/env python3
import socket
import struct
import zlib
import time

LISTEN_ADDRESS = "10.0.0.2"
LISTEN_PORT = 5009

OUTFILE = "received_file.mp4"

TYPE_DATA = 0
TYPE_EOF  = 1

HDR_FMT = "!BIHI"
HDR_SIZE = struct.calcsize(HDR_FMT)

# ACK format: b'A' + ack_base(u32) + sack_len(u16) + sack_bytes
ACK_HDR_FMT = "!cIH"
ACK_HDR_SIZE = struct.calcsize(ACK_HDR_FMT)

# Final checksum: b'F' + crc32(u32)
FILECRC_FMT = "!cI"

# Receiver buffering / SACK settings
SACK_BITS = 4096              # how many packets after ack_base to report in SACK
SACK_BYTES = (SACK_BITS + 7) // 8
MAX_BUFFER_PKTS = 20000       # safety cap for out-of-order buffer dict

# ACK pacing
ACK_EVERY_PKTS = 64
ACK_EVERY_SEC = 0.01


def build_ack(ack_base: int, received_after_base: set):
    """
    ack_base = highest contiguous received (we have all 0..ack_base)
    received_after_base contains seq > ack_base that are buffered/received.
    Build bitmask for (ack_base+1 .. ack_base+SACK_BITS)
    """
    sack = bytearray(SACK_BYTES)
    start = ack_base + 1
    end = ack_base + 1 + SACK_BITS

    for s in received_after_base:
        if s < start or s >= end:
            continue
        i = s - start
        sack[i >> 3] |= (1 << (i & 7))

    hdr = struct.pack(ACK_HDR_FMT, b"A", ack_base, len(sack))
    return hdr + bytes(sack)


def main():
    expected = 0
    file_crc = 0

    # Out-of-order buffer: seq -> bytes(payload)
    buf = {}

    # For SACK reporting: keep a set of seqs currently buffered (>ack_base)
    buffered_seqs = set()

    last_ack_time = 0.0
    pkts_since_ack = 0

    print(f"Listening UDP on {LISTEN_ADDRESS}:{LISTEN_PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Big receive buffer
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64 * 1024 * 1024)
        sock.bind((LISTEN_ADDRESS, LISTEN_PORT))

        rx_buf = bytearray(2048)
        mv = memoryview(rx_buf)

        start = time.time()

        with open(OUTFILE, "wb") as fout:
            while True:
                nbytes, addr = sock.recvfrom_into(rx_buf)
                if nbytes < HDR_SIZE:
                    continue

                pkt_type, seq, payload_len, crc = struct.unpack(HDR_FMT, mv[:HDR_SIZE])

                if pkt_type == TYPE_DATA:
                    end = HDR_SIZE + payload_len
                    if end > nbytes:
                        continue  # malformed/truncated

                    payload = bytes(mv[HDR_SIZE:end])  # copy only payload once

                    # CRC check
                    if (zlib.crc32(payload) & 0xFFFFFFFF) != crc:
                        # corrupted; ignore (sender will retransmit)
                        continue

                    # If already written (seq < expected), it's a duplicate; ignore but can still ACK
                    if seq < expected:
                        pkts_since_ack += 1
                    else:
                        # Buffer or accept
                        if seq == expected:
                            # write in-order
                            fout.write(payload)
                            file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF
                            expected += 1

                            # flush any buffered contiguous packets
                            while expected in buf:
                                p = buf.pop(expected)
                                buffered_seqs.discard(expected)
                                fout.write(p)
                                file_crc = zlib.crc32(p, file_crc) & 0xFFFFFFFF
                                expected += 1
                        else:
                            # out-of-order; buffer if not too large
                            if seq not in buf:
                                if len(buf) < MAX_BUFFER_PKTS:
                                    buf[seq] = payload
                                    buffered_seqs.add(seq)
                                # else: drop (buffer full) -> sender will retransmit
                            pkts_since_ack += 1

                    # Send ACK occasionally (packet-based or time-based)
                    now = time.time()
                    if pkts_since_ack >= ACK_EVERY_PKTS or (now - last_ack_time) >= ACK_EVERY_SEC:
                        ack_base = expected - 1
                        ack_pkt = build_ack(ack_base, buffered_seqs)
                        sock.sendto(ack_pkt, addr)
                        pkts_since_ack = 0
                        last_ack_time = now

                    # light progress print
                    if expected % 50000 == 0 and expected > 0:
                        elapsed = time.time() - start
                        mb = (expected * 1461) / (1024 * 1024)
                        print(f"Written pkts={expected}  (~{mb:.1f} MiB)  t={elapsed:.2f}s", end="\r")

                elif pkt_type == TYPE_EOF:
                    # Final ACK to help sender finish window
                    ack_base = expected - 1
                    ack_pkt = build_ack(ack_base, buffered_seqs)
                    sock.sendto(ack_pkt, addr)

                    # Send final CRC
                    sock.sendto(struct.pack(FILECRC_FMT, b"F", file_crc), addr)
                    print(f"\nEOF received. Wrote: {OUTFILE}")
                    print(f"Final file CRC32: 0x{file_crc:08X}")
                    break

        elapsed = time.time() - start
        approx_bytes = expected * 1461
        mbps = (approx_bytes * 8 / elapsed) / 1e6 if elapsed > 0 else 0
        print(f"Elapsed: {elapsed:.3f}s  Approx receive rate: {mbps:.2f} Mb/s")


if __name__ == "__main__":
    main()

