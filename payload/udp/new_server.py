# =========================
# udp_server.py  (RECEIVER)
# =========================
import socket
import struct
import zlib

LISTEN_ADDRESS = "10.0.0.2"
LISTEN_PORT = 5009
OUTFILE = "received_file.mp4"

TYPE_DATA = 0
TYPE_EOF  = 1

# type(1) seq(4) len(2) crc32(4)  => 11 bytes
HDR_FMT = "!BIHI"
HDR_SIZE = struct.calcsize(HDR_FMT)

# Tune these
RCVBUF_BYTES = 32 * 1024 * 1024   # 32MB UDP receive buffer
FILEBUF_BYTES = 4 * 1024 * 1024   # 4MB file write buffer
RECV_BUF_BYTES = 2048             # enough for header + ~1500 payload

def main():
    expected_seq = 0
    file_crc = 0

    print(f"Listening UDP on {LISTEN_ADDRESS}:{LISTEN_PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUF_BYTES)
        sock.bind((LISTEN_ADDRESS, LISTEN_PORT))

        buf = bytearray(RECV_BUF_BYTES)
        mv = memoryview(buf)

        with open(OUTFILE, "wb", buffering=FILEBUF_BYTES) as fout:
            while True:
                nbytes, addr = sock.recvfrom_into(mv)
                if nbytes < HDR_SIZE:
                    continue

                pkt_type, seq, payload_len, crc = struct.unpack(HDR_FMT, mv[:HDR_SIZE])
                end = HDR_SIZE + payload_len
                if end > nbytes:
                    continue

                if pkt_type == TYPE_DATA:
                    payload = mv[HDR_SIZE:end]

                    # Verify CRC32 of payload
                    calc = zlib.crc32(payload) & 0xFFFFFFFF
                    if calc != crc:
                        # drop corrupted packet
                        continue

                    # Strict in-order write (no seq jumping!)
                    if seq == expected_seq:
                        fout.write(payload)
                        file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF
                        expected_seq += 1

                        if expected_seq % 2000 == 0:
                            print(f"Received seq={seq}", end="\r")
                    else:
                        # out-of-order or missing packet -> ignore
                        # (pacing on sender keeps this rare)
                        continue

                elif pkt_type == TYPE_EOF:
                    sock.sendto(b"F" + struct.pack("!I", file_crc), addr)
                    print(f"\nEOF received. Wrote: {OUTFILE}")
                    print(f"Final file CRC32: 0x{file_crc:08X}")
                    break

if __name__ == "__main__":
    main()

