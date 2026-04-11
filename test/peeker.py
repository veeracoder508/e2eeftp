""" 
This file is for test porpus only. Use this for ethical use only!

To check the encription of the server by using a socket sniffer.
"""
import socket
import threading

# Configuration
LISTEN_PORT = 8080  # Port A (The one your app sends to)
TARGET_PORT = 9090  # Port B (The one the receiver is listening on)
TARGET_HOST = '127.0.0.1'

def handle_client(source_conn):
    # Connect to the actual destination (Port B)
    target_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_conn.connect((TARGET_HOST, TARGET_PORT))
    
    def forward(source, destination, label):
        while True:
            try:
                data = source.recv(4096)
                if len(data) == 0:
                    break
                
                # PRINT THE CONTENT
                print(f"[{label}] {data.decode('utf-8', errors='replace')}")
                
                destination.sendall(data)
            except:
                break

    # Start two threads to allow bidirectional communication
    # Thread 1: Port A -> Port B
    # Thread 2: Port B -> Port A
    t1 = threading.Thread(target=forward, args=(source_conn, target_conn, "A -> B"))
    t2 = threading.Thread(target=forward, args=(target_conn, source_conn, "B -> A"))
    
    t1.start()
    t2.start()

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', LISTEN_PORT))
    server.listen(5)
    print(f"Proxy started. Send data to Port {LISTEN_PORT} to forward to {TARGET_PORT}")

    while True:
        client_sock, addr = server.accept()
        print(f"Connection received from {addr}")
        handle_client(client_sock)

if __name__ == "__main__":
    start_proxy()