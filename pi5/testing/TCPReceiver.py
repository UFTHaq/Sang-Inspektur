import socket

HOST = "10.20.0.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Waiting for connection...")
    conn, addr = s.accept()
    print("Connected by", addr)

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("Received:", data.decode().strip())
