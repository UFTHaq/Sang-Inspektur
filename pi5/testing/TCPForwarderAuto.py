import socket
import threading
import time
import subprocess

# --- Laptop TCP server settings ---
LAPTOP_HOST = "0.0.0.0"  # Pi5 listens on all interfaces
LAPTOP_PORT = 5000

# --- ESP32-S3 TCP client settings ---
ESP32S3_SSID  = "ESP32S3_AP"
ESP32S3_PASS  = "12345678"
ESP32S3_HOST  = "192.168.4.1"  # ESP32S3 AP IP
ESP32S3_PORT  = 5001           # ESP32S3 listening port

# Global connection to ESP32S3
esp32s3_socket = None
esp32s3_lock = threading.Lock()

# Track last message for change detection
last_message = None

def wifi_connect():
    """Ensure Pi5 is connected to ESP32S3 Wi-Fi AP."""
    result = subprocess.getoutput("nmcli -t -f active,ssid dev wifi | egrep '^yes'")
    if ESP32S3_SSID in result:
        return True

    try:
        subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ESP32S3_SSID, "password", ESP32S3_PASS],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def wait_for_ip():
    """Wait until DHCP gives Pi5 an IP address."""
    for _ in range(10):
        ip = subprocess.getoutput("hostname -I").strip()
        if ip:
            return True
        time.sleep(1)
    return False

def connect_esp32():
    """Try to connect to ESP32-S3 continuously"""
    global esp32s3_socket
    while True:
        if not wifi_connect():
            print("Waiting for ESP32S3 AP...")
            time.sleep(2)
            continue

        if not wait_for_ip():
            print("No IP yet, retrying...")
            time.sleep(2)
            continue

        try:
            with esp32s3_lock:
                if esp32s3_socket:
                    esp32s3_socket.close()
                esp32s3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                esp32s3_socket.settimeout(5)
                esp32s3_socket.connect((ESP32S3_HOST, ESP32S3_PORT))
                print("Connected to ESP32-S3")
            break
        except Exception as e:
            print("ESP32 connect failed, retrying in 3s...", e)
            time.sleep(3)

def handle_laptop_client(conn, addr):
    """Receive data from laptop and forward to ESP32-S3"""
    global last_message
    print("Laptop connected:", addr)
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("Laptop disconnected:", addr)
                    break

                msg = data.decode().strip()
                print("From laptop:", msg)

                # Send only if message changed
                if msg != last_message:
                    with esp32s3_lock:
                        if esp32s3_socket:
                            esp32s3_socket.sendall(msg.encode())
                            last_message = msg

            except Exception as e:
                print("Error handling laptop client:", e)
                break

def keep_alive_loop():
    """Send keepalive every 1s"""
    global last_message
    while True:
        time.sleep(1)
        with esp32s3_lock:
            if esp32s3_socket:
                try:
                    esp32s3_socket.sendall(b"keepalive")
                except Exception as e:
                    print("Keepalive failed:", e)
                    last_message = None
                    connect_esp32()

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
    # Connect ESP32 in background
    threading.Thread(target=connect_esp32, daemon=True).start()

    # Start keep-alive thread
    threading.Thread(target=keep_alive_loop, daemon=True).start()

    # Start laptop TCP server
    laptop_server()
