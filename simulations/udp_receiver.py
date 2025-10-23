import socket

def udp_receiver(listen_ip="10.0.0.1", port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))
    print(f"Listening for UDP packets on {listen_ip}:{port}")

    while True:
        data, addr = sock.recvfrom(2048)
        print(f"Received from {addr}: {data.decode()}")

if __name__ == "__main__":
    udp_receiver()

