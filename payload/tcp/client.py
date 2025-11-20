import socket

SERVER_ADDRESS = '10.0.0.1'
SERVER_PORT = 5009

if __name__ == "__main__":

    # Open socket connection to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_ADDRESS, SERVER_PORT))
        print('Connected!')

        # Send text file line by line 
        with open('test_video.mp4','rb') as fh:
            print('Sending file...')
            while True:
                data = fh.read(1024)
                if not data:
                    break 

                sock.sendall(data) # Send encoded bytes
    print('File transfer complete!')
