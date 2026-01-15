import socket
import time

def udp_receiver(listen_ip="10.0.0.1", port=5005, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))
    sock.settimeout(timeout)

    print(f"Listening on {listen_ip}:{port} for {timeout} seconds...")
    total_bytes = 0
    packets = 0
    start_time = None  # Timer will start on first packet

    try:
        while True:
            data, _ = sock.recvfrom(65535)
            if start_time is None:
                start_time = time.time()  # Start timing on first packet
            total_bytes += len(data)
            packets += 1
    except socket.timeout:
        pass  # stop when timeout reached

    if packets > 0:
        elapsed = time.time() - start_time
        data_rate_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
        data_rate_MBps = data_rate_mbps / 8
        print(f"\nReceived {packets} packets ({total_bytes} bytes) in {elapsed:.2f} s")
        print(f"Measured receive rate: {data_rate_MBps:.2f} MB/s")
    else:
        print("No data received (no packets arrived before timeout).")

if __name__ == "__main__":
    udp_receiver()

