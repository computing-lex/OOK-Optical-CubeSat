import socket

def udp_receiver(host="192.168.10.2", port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Listening on {host}:{port}")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received from {addr}: {data.decode('utf-8')}")

if __name__ == "__main__":
    udp_receiver()
