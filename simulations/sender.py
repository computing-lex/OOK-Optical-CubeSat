import socket
import time
import struct

# Configuration
DEST_IP = '127.0.0.1'
DEST_PORT = 5005
PACKET_SIZE = 1472  # bytes
TOTAL_FRAMES = 50
DATA_RATE_Mbps = 100  # target data rate in Mbps

# Calculate bytes per second and delay between packets
bytes_per_sec = (DATA_RATE_Mbps * 1_000_000) // 8  # convert Mbps to Bytes per second
delay_per_packet = PACKET_SIZE / bytes_per_sec  # seconds

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Starting UDP sender to {DEST_IP}:{DEST_PORT}")
print(f"Packet size: {PACKET_SIZE} bytes, Total frames: {TOTAL_FRAMES}, Target data rate: {DATA_RATE_Mbps} Mbps")

for seq in range(1, TOTAL_FRAMES + 1):
    # Packet payload: sequence number (4 bytes) + padding
    payload = struct.pack('!I', seq) + b'\x00' * (PACKET_SIZE - 4)
    start_time = time.time()
    sock.sendto(payload, (DEST_IP, DEST_PORT))
    elapsed = time.time() - start_time
    print(f"Frame {seq:04d} sent")
    # Sleep to maintain data rate minus elapsed send time
    time_to_sleep = delay_per_packet - elapsed
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

print("Transmission complete.")
sock.close()
