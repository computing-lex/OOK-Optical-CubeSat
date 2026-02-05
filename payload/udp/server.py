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

def main():
    expected_seq = 0
    file_crc = 0

    print(f"Listening UDP on {LISTEN_ADDRESS}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((LISTEN_ADDRESS, LISTEN_PORT))

        with open(OUTFILE, "wb") as fout:
            while True:
                data, addr = sock.recvfrom(65535)
                if len(data) < HDR_SIZE:
                    continue

                pkt_type, seq, payload_len, crc = struct.unpack(HDR_FMT, data[:HDR_SIZE])
                payload = data[HDR_SIZE:HDR_SIZE + payload_len]

                if pkt_type == TYPE_DATA:
                    # Verify payload length
                    if len(payload) != payload_len:
                        # ignore malformed packet
                        continue

                    # Verify CRC32 of payload
                    calc = zlib.crc32(payload) & 0xFFFFFFFF
                    if calc != crc:
                        print(f"Checksum MISMATCH on packet {seq}")
                        # corrupted packet: do not ACK (client will retry)
                        continue

                    # Simple in-order receiver:
                    if seq == expected_seq:
                        fout.write(payload)
                        file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF
                        # Update display
                        if seq % 50 == 0:
                            print(f"Recieved seq={seq}", end="\r")
                        expected_seq += 1
                        # ACK this seq
                        # sock.sendto(b"A" + struct.pack("!I", seq), addr)
                    else:
                        # If out of order/duplicate, ACK last good (helps stop re-sends)
                        print(f"Recieved seq={seq} Expected SEQ number={expected_seq}", end="\r")
                        expected_seq=seq
                        #last_good = expected_seq - 1 if expected_seq > 0 else 0
                        #sock.sendto(b"A" + struct.pack("!I", last_good), addr)

                elif pkt_type == TYPE_EOF:
                    # Send final file checksum back
                    sock.sendto(b"F" + struct.pack("!I", file_crc), addr)
                    print(f"EOF received. Wrote: {OUTFILE}")
                    print(f"Final file CRC32: 0x{file_crc:08X}")
                    break

if __name__ == "__main__":
    main()

