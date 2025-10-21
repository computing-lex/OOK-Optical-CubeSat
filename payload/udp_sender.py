import socket
import time

def udp_sender(target_ip="10.0.0.1", port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        message = "Hello over fiber!"
        sock.sendto(message.encode(), (target_ip, port))
        print(f"Sent: {message}")
        time.sleep(1)

if __name__ == "__main__":
    udp_sender()

