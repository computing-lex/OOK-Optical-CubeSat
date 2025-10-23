import socket
import time
import argparse

def tcp_receiver(bind_ip, port, echo=False):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, port))
    server.listen(1)

    print(f"[RX] Listening on {bind_ip}:{port} (echo={echo})...")
    conn, addr = server.accept()
    print(f"[RX] Connection established from {addr}")

    total_bytes = 0
    start_time = time.perf_counter()
    while True:
        data = conn.recv(4096)
        if not data:
            break
        total_bytes += len(data)
        if echo:
            conn.sendall(data)  # echo back to sender

    end_time = time.perf_counter()
    duration = end_time - start_time
    mbps = (total_bytes * 8) / (duration * 1e6)

    print("\n--- Receiver Summary ---")
    print(f"Total data received:  {total_bytes / 1e6:.2f} MB")
    print(f"Total duration:       {duration:.3f} s")
    print(f"Measured Rx rate:     {mbps:.2f} Mbps")

    conn.close()
    server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Receiver")
    parser.add_argument("--ip", required=True, help="Receiver IP address")
    parser.add_argument("--port", type=int, default=5005, help="Listening TCP port")
    parser.add_argument("--echo", action="store_true", help="Echo data back to sender")
    args = parser.parse_args()

    tcp_receiver(args.ip, args.port, args.echo)

