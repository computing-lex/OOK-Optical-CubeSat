import socket
import struct
import time

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 5005
PACKET_SIZE = 1472
TOTAL_FRAMES = 50

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
sock.settimeout(5)  # timeout to stop after inactivity

print(f"Listening for UDP packets on {LISTEN_IP}:{LISTEN_PORT}")

received_frames = set()
total_bytes = 0
start_time = None

while len(received_frames) < TOTAL_FRAMES:
    try:
        data, addr = sock.recvfrom(2048)
        if start_time is None:
            start_time = time.time()
        if len(data) != PACKET_SIZE:
            print(f"Warning: received packet of unexpected size {len(data)} bytes")
        seq_num = struct.unpack('!I', data[:4])[0]
        received_frames.add(seq_num)
        total_bytes += len(data)
        print(f"Received frame {seq_num:04d} from {addr}")
    except socket.timeout:
        print("Socket timeout, stopping receive.")
        break

elapsed = time.time() - start_time if start_time else 0.001  # avoid div by zero
missing_frames = set(range(1, TOTAL_FRAMES + 1)) - received_frames
errors = len(missing_frames)
throughput_mbps = (total_bytes * 8) / (elapsed * 1_000_000)

print("\n--- Reception Summary ---")
print(f"Total frames expected: {TOTAL_FRAMES}")
print(f"Total frames received: {len(received_frames)}")
print(f"Frames lost (errors): {errors}")
print(f"Estimated throughput: {throughput_mbps:.2f} Mbps")
print(f"Elapsed time: {elapsed:.3f} seconds")

sock.close()
