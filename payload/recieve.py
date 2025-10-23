#!/usr/bin/env python3
# fiber_speed_test_receiver.py
import socket
import argparse

def udp_receiver(listen_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))
    print(f"[RX] Listening on {listen_ip}:{port} (echoing payloads)")

    try:
        while True:
            data, addr = sock.recvfrom(65536)
            # echo raw packet back unchanged (fast path)
            sock.sendto(data, addr)
    except KeyboardInterrupt:
        print("\n[RX] Stopping")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", default="10.0.0.1", help="Receiver IP")
    parser.add_argument("--port", type=int, default=5005, help="UDP port")
    args = parser.parse_args()
    udp_receiver(args.listen, args.port)

