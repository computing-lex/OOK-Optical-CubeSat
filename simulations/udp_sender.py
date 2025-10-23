import socket
import time

def udp_sender(interface_ip="10.0.0.2", target_ip="10.0.0.1", port=5005):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to your specific network interface IP (fiber NIC)
    sock.bind((interface_ip, 0))

    print(f"Starting UDP sender from {interface_ip} to {target_ip}:{port}")
    
    while True:
        message = "Hello over fiber!"
        try:
            sock.sendto(message.encode(), (target_ip, port))
            print(f"Sent: {message}")
        except OSError as e:
            print(f"Error sending packet: {e}")
        time.sleep(1)

if __name__ == "__main__":
    udp_sender()

