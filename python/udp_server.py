import socket

UDP_IP = "" # Set to target IP
UDP_PORT = 8000 # Change to correct port

test_message = "Sending!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.sendto(test_message.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent packet to {UDP_IP}:{UDP_PORT}: {test_message}")
finally:
    sock.close()