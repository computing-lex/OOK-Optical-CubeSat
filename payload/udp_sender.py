import socket
import time

def udp_sender(target_ip="192.168.10.2", port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    counter = 0
    print(f"Sending UDP packets to {target_ip}:{port}")

    while True:
        message = f"Hello from sender! Packet #{counter}"
        sock.sendto(message.encode("utf-8"), (target_ip, port))
        print(f"Sent: {message}")
        counter += 1
        time.sleep(1)

if __name__ == "__main__":
    udp_sender()
