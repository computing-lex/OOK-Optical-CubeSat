import socket
import struct
import zlib

LISTEN_ADDRESS = "10.0.0.2"
LISTEN_PORT = 5009

OUTFILE = "received_file.mp4"

TYPE_DATA = 0
TYPE_EOF  = 1

HDR_FMT = "!BIHI"
HDR_SIZE = struct.calcsize(HDR_FMT)

def main():
    highest_seq = -1
    received_unique = set()
    file_crc = 0

    print(f"Listening UDP on {LISTEN_ADDRESS}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
        sock.bind((LISTEN_ADDRESS, LISTEN_PORT))

        rx_buf = bytearray(2048)
        mv = memoryview(rx_buf)

        with open(OUTFILE, "wb") as fout:
            while True:
                nbytes, addr = sock.recvfrom_into(rx_buf)
                if nbytes < HDR_SIZE:
                    continue

                pkt_type, seq, payload_len, crc = struct.unpack(HDR_FMT, mv[:HDR_SIZE])
                payload = mv[HDR_SIZE:HDR_SIZE + payload_len]

                if pkt_type == TYPE_DATA:
                    if seq not in received_unique:
                        received_unique.add(seq)

                        if seq > highest_seq:
                            highest_seq = seq

                        # write data (arrival order)
                        fout.write(payload)

                        file_crc = zlib.crc32(payload, file_crc) & 0xFFFFFFFF

                        if seq % 5000 == 0:
                            print(f"Received seq={seq}", end="\r")

                elif pkt_type == TYPE_EOF:
                    sock.sendto(b"F" + struct.pack("!I", file_crc), addr)
                    break

    # ---- DROP CALCULATION ----
    total_expected = highest_seq + 1
    total_received = len(received_unique)
    total_dropped = total_expected - total_received

    if total_expected > 0:
        drop_percent = (total_dropped / total_expected) * 100
    else:
        drop_percent = 0

    print("\nTransfer complete.")
    print(f"Highest sequence received: {highest_seq}")
    print(f"Total expected packets: {total_expected}")
    print(f"Unique packets received: {total_received}")
    print(f"Packets dropped: {total_dropped}")
    print(f"Drop percentage: {drop_percent:.2f}%")

if __name__ == "__main__":
    main()

