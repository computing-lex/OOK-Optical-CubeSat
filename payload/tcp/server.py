import socket

# Server config
LISTEN_ADDRESS = '0.0.0.0'  # Standard loopback interface address (localhost)
LISTEN_PORT = 5002 # Listening port 

if __name__ == "__main__":

    # Create listening socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to address and port to listen
    server_socket.bind((LISTEN_ADDRESS, LISTEN_PORT))
    server_socket.listen(1) # Listen allowing 1 connection at a time

    print(f'Listening on {LISTEN_ADDRESS}:{LISTEN_PORT}')

    while True: # Continuously accept new connections
        client_socket, address = server_socket.accept() 
        print(f'Accepted connection from {address[0]}:{address[1]}')

        with client_socket:
            # Receive file contents in 1KB chunks
            print('Receiving...')
            chunk_buffer = client_socket.recv(1024)

            # Write bytes to target file          
            with open('received_file', 'wb') as fout:
                while chunk_buffer:
                    print('Writing chunk...', end='\r')
                    fout.write(chunk_buffer)
                    chunk_buffer = client_socket.recv(1024)

            print('File received!')