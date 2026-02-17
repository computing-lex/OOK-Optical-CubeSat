import socket
import struct
import zlib

LISTEN_ADDRESS = "10.0.0.2"
LISTEN_PORT = 5009

OUTFILE = "received_file.mp4"

TYPE_DATA = 0
TYPE_EOF  = 1

HDR_FMT = "!BIHI"  # type(1) seq(4) len(2) crc32(4)
HDR_SIZE = struct.calcsize(HDR_FMT)

# Optional: buffer writes to reduce disk overhead
WRITE_BUFFER_BYTES = 1 * 1024 * 1024  # 1 MiB

def main():
    expected_seq = 0
    dropped_pack = 0
    file_crc = 0

    print(f"Listening UDP on {LISTEN_ADDRESS}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Bigger receive buffer (critical for high-rate UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)

        sock.bind((LISTEN_ADDRESS, LISTEN_PORT))

        # Pre-allocate receive buffer to avoid allocations per packet
        rx_buf = bytearray(2048)  # enough for header+payload (<= 1500-ish)
        mv = memoryview(rx_buf)

        write_buf = bytearray()

        with open(OUTFILE, "wb") as fout:
            while True:
                nbytes, addr = sock.recvfrom_into(rx_buf)
                if nbytes < HDR_SIZE:
                    continue

                pkt_type, seq, payload_len, crc = struct.unpack(HDR_FMT, mv[:HDR_SIZE])
                end = HDR_SIZE + payload_len
                if end > nbytes:
                    # malformed / truncated
                    continue

                payload = mv[HDR_SIZE:end]

                if pkt_type == TYPE_DATA:
                    # Verify payload length
                    if payload_len < 0:
                        continue

                    # Verify CRC32 of payload
                    calc = zlib.crc32(payload) & 0xFFFFFFFF
                    if calc != crc:
                        # corrupted packet
                        continue

                    # Strict in-order receiver: only accept expected seq
                    if seq == expected_seq:
                        # Buffer writes (faster than lots of small writes)
                        write_buf += payload
                        if len(write_buf) >= WRITE_BUFFER_BYTES:
                            fout.write(write_buf)
                            write_buf.clear()

                        file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF

                        # Print less often (printing is expensive)
                        if seq % 5000 == 0:
                            print(f"Received seq={seq} Dropped packets={dropped_pack}", end="\r")

                        expected_seq += 1
                        # Optional ACKs (still commented, as in your original)
                        # sock.sendto(b"A" + struct.pack("!I", seq), addr)

                    else:
                        # Out-of-order or duplicate: count it, but DO NOT advance expected_seq
                        dropped_pack += 1
                        if dropped_pack % 5000 == 0:
                            print(f"Dropped packets={dropped_pack} (last seq={seq}, expected={expected_seq})", end="\r")
                        # Optional: ACK last good (still commented)
                        # last_good = expected_seq - 1 if expected_seq > 0 else 0
                        # sock.sendto(b"A" + struct.pack("!I", last_good), addr)

                elif pkt_type == TYPE_EOF:
                    # Flush remaining buffered writes
                    if write_buf:
                        fout.write(write_buf)
                        write_buf.clear()

                    # Send final file checksum back
                    sock.sendto(b"F" + struct.pack("!I", file_crc), addr)
                    print(f"\nEOF received. Wrote: {OUTFILE}")
                    print(f"Final file CRC32: 0x{file_crc:08X}")
                    print(f"Dropped packets (out-of-order/duplicates seen): {dropped_pack}")
                    break

if __name__ == "__main__":
    main()

