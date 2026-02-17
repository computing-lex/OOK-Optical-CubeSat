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

# Buffer writes to reduce disk overhead
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
        rx_buf = bytearray(2048)  # enough for header+payload (<= ~1500)
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
                    continue  # malformed/truncated

                payload = mv[HDR_SIZE:end]

                if pkt_type == TYPE_DATA:
                    # Verify CRC32 of payload
                    calc = zlib.crc32(payload) & 0xFFFFFFFF
                    if calc != crc:
                        continue  # corrupted

                    # OPTION 1: streaming receiver (does NOT stall on missing packet)
                    # Accept any new seq >= expected_seq. Count gaps as "dropped".
                    if seq >= expected_seq:
                        if seq > expected_seq:
                            dropped_pack += (seq - expected_seq)

                        # write payload immediately (arrival order)
                        write_buf += payload
                        if len(write_buf) >= WRITE_BUFFER_BYTES:
                            fout.write(write_buf)
                            write_buf.clear()

                        file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF

                        if seq % 5000 == 0:
                            print(f"Received seq={seq} Dropped packets={dropped_pack}", end="\r")

                        expected_seq = seq + 1
                    else:
                        # old/duplicate packet
                        dropped_pack += 1

                elif pkt_type == TYPE_EOF:
                    # Flush remaining buffered writes
                    if write_buf:
                        fout.write(write_buf)
                        write_buf.clear()

                    # Send final file checksum back
                    sock.sendto(b"F" + struct.pack("!I", file_crc), addr)
                    print(f"\nEOF received. Wrote: {OUTFILE}")
                    print(f"Final file CRC32: 0x{file_crc:08X}")
                    print(f"Dropped packets (gaps + duplicates): {dropped_pack}")
                    break

if __name__ == "__main__":
    main()

