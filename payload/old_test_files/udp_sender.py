import socket
import time

def udp_sender(target_ip="10.0.0.1", port=5005, duration=5, payload_size=1472):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b"x" * payload_size  # payload size in bytes

    print(f"Sending to {target_ip}:{port} for {duration} seconds...")
    start_time = time.time()
    packets = 0
    total_bytes = 0

    while time.time() - start_time < duration:
        sock.sendto(payload, (target_ip, port))
        packets += 1
        total_bytes += len(payload)

    elapsed = time.time() - start_time
    data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
    data_rate_MBps = data_rate_mbps / 8
    print(f"\nSent {packets} packets ({total_bytes} bytes) in {elapsed:.2f} s")
    print(f"Measured transmit rate: {data_rate_MBps:.2f} MB/s")

if __name__ == "__main__":
    udp_sender()

