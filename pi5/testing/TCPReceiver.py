import socket
import threading
import time

# --- Laptop TCP server settings ---
LAPTOP_HOST = "0.0.0.0"  # Pi5 listens on all interfaces
LAPTOP_PORT = 5000

# --- ESP32-S3 TCP client settings ---
ESP32_HOST = "192.168.4.1"  # Replace with your ESP32-S3 AP IP
ESP32_PORT = 5001           # Replace with ESP32-S3 listening port

# Global connection to ESP32
esp32_socket = None
esp32_lock = threading.Lock()

def connect_esp32():
    """Try to connect to ESP32-S3 continuously"""
    global esp32_socket
    while True:
        try:
            with esp32_lock:
                if esp32_socket:
                    esp32_socket.close()
                esp32_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                esp32_socket.connect((ESP32_HOST, ESP32_PORT))
                print("Connected to ESP32-S3")
            break
        except Exception as e:
            print("ESP32 connect failed, retrying in 3s...", e)
            time.sleep(3)

def handle_laptop_client(conn, addr):
    """Receive data from laptop and forward to ESP32-S3"""
    print("Laptop connected:", addr)
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("Laptop disconnected:", addr)
                    break
                print("Received from laptop:", data.decode().strip())

                # Forward to ESP32-S3
                with esp32_lock:
                    if esp32_socket:
                        esp32_socket.sendall(data)
            except Exception as e:
                print("Error handling laptop client:", e)
                break

def laptop_server():
    """TCP server for laptop"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LAPTOP_HOST, LAPTOP_PORT))
        s.listen()
        print(f"Waiting for laptop on {LAPTOP_HOST}:{LAPTOP_PORT}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_laptop_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    # Connect ESP32 in a separate thread
    threading.Thread(target=connect_esp32, daemon=True).start()
    
    # Start laptop TCP server
    laptop_server()
