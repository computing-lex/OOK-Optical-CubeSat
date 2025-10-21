import socket

UDP_IP = "" # Set to target IP
UDP_PORT = 8000 # Change to correct port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for packets on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Recieved packet from {addr}: {data.decode('utf-8')}")