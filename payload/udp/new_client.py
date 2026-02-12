# ======================
# udp_client.py (SENDER)
# ======================
import os
import socket
import struct
import sys
import time
import zlib

SERVER_ADDRESS = "10.0.0.2"
SERVER_PORT = 5009

TYPE_DATA = 0
TYPE_EOF  = 1

HDR_FMT = "!BIHI"
HDR_SIZE = struct.calcsize(HDR_FMT)

# With MTU 1500, this is the sweet spot (no fragmentation)
CHUNK_SIZE = 1460

# Buffers
SNDBUF_BYTES = 16 * 1024 * 1024   # 16MB send buffer
READBUF_BYTES = 4 * 1024 * 1024   # 4MB file read buffer

# Pacing (set to None to disable)
TARGET_MBPS = 900   # try 800–950; raise until loss starts
PACE_EVERY = 64     # pace every N packets (reduces time.sleep overhead)

SOCKET_TIMEOUT = 0.25
MAX_RETRIES = 50

def recv_msg(sock):
    data = sock.recv(64)
    if not data:
        return None
    if data[0:1] == b"F" and len(data) >= 5:
        (crc,) = struct.unpack("!I", data[1:5])
        return ("FILECRC", crc)
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 udp_client.py <file_to_send>")
        raise SystemExit(2)

    filename = sys.argv[1]
    filesize = os.path.getsize(filename)

    # Whole-file CRC for end-to-end verification
    file_crc = 0
    with open(filename, "rb", buffering=READBUF_BYTES) as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            file_crc = zlib.crc32(b, file_crc) & 0xFFFFFFFF

    print(f"Sending: {filename} ({filesize} bytes)")
    print(f"Local file CRC32: 0x{file_crc:08X}")

    # Pacing math
    if TARGET_MBPS is not None:
        bits_per_pkt = (HDR_SIZE + CHUNK_SIZE) * 8
        pkts_per_sec = (TARGET_MBPS * 1e6) / bits_per_pkt
        sleep_per_pkt = 1.0 / pkts_per_sec
    else:
        sleep_per_pkt = 0.0

    start = time.perf_counter()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SNDBUF_BYTES)
        sock.settimeout(SOCKET_TIMEOUT)
        sock.connect((SERVER_ADDRESS, SERVER_PORT))

        seq = 0
        sent_bytes = 0
        pace_counter = 0

        with open(filename, "rb", buffering=READBUF_BYTES) as fh:
            while True:
                payload = fh.read(CHUNK_SIZE)
                if not payload:
                    break

                crc = zlib.crc32(payload) & 0xFFFFFFFF
                header = struct.pack(HDR_FMT, TYPE_DATA, seq, len(payload), crc)
                sock.send(header + payload)

                sent_bytes += len(payload)
                seq += 1

                if seq % 2000 == 0:
                    print(f"Sent seq={seq} progress={sent_bytes}/{filesize}", end="\r")

                # Light-weight pacing
                if sleep_per_pkt > 0:
                    pace_counter += 1
                    if pace_counter >= PACE_EVERY:
                        time.sleep(sleep_per_pkt * PACE_EVERY)
                        pace_counter = 0

        elapsed = time.perf_counter() - start
        mbps = (filesize * 8 / elapsed) / 1e6
        print(f"\nData sent in {elapsed:.3f}s  =>  {mbps:.1f} Mbps")

        # Send EOF and wait for final checksum
        eof = struct.pack(HDR_FMT, TYPE_EOF, seq, 0, 0)

        retries = 0
        while True:
            sock.send(eof)
            try:
                msg = recv_msg(sock)
                if msg and msg[0] == "FILECRC":
                    remote_crc = msg[1]
                    print(f"Remote CRC32: 0x{remote_crc:08X}")
                    if remote_crc == file_crc:
                        print("End-to-end checksum MATCH.")
                    else:
                        print("Checksum MISMATCH (loss/corruption likely).")
                    break
            except socket.timeout:
                retries += 1
                if retries > MAX_RETRIES:
                    raise RuntimeError("Too many retries waiting for final checksum.")

if __name__ == "__main__":
    main()

