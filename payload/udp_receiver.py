import socket

def udp_receiver(port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"Listening on port {port} (all interfaces)")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received from {addr}: {data.decode('utf-8')}")

if __name__ == "__main__":
    udp_receiver()

