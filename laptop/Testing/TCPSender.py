import sys
import pygame
import socket
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer


class GamepadWindow(QWidget):
    def __init__(self):
        super().__init__()

        # --- UI setup ---
        self.setWindowTitle("Gamepad + PySide6")
        self.label = QLabel("Waiting for gamepad input...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # --- pygame init ---
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.label.setText(f"Gamepad connected: {self.joystick.get_name()}")
        else:
            self.joystick = None
            self.label.setText("No gamepad detected")

        # --- TCP setup (client to Pi 5) ---
        self.server_ip = "10.20.0.2"   # <-- change to your Pi 5 LAN IP
        self.server_port = 5000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.server_ip, self.server_port))
            print("Connected to Pi 5")
        except Exception as e:
            print("TCP connect failed:", e)
            self.sock = None

        # --- Timer to poll gamepad ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_gamepad)
        self.timer.start(50)  # poll every 50ms

    def poll_gamepad(self):
        if not self.joystick:
            return

        pygame.event.pump()  # process events internally

        # Axes
        lx = self.joystick.get_axis(0)
        ly = self.joystick.get_axis(1)
        rx = self.joystick.get_axis(2)
        ry = self.joystick.get_axis(3)

        # L2 R2 Analog
        l2 = self.joystick.get_axis(4)  # usually L2 trigger
        r2 = self.joystick.get_axis(5)  # usually R2 trigger

        # Buttons (example for 4 buttons + shoulders)
        a = self.joystick.get_button(0)
        b = self.joystick.get_button(1)
        x = self.joystick.get_button(2)
        y = self.joystick.get_button(3)

        # L1 R1
        l1 = self.joystick.get_button(9)
        r1 = self.joystick.get_button(10)

        # Direct Pad
        du = self.joystick.get_button(11)
        dd = self.joystick.get_button(12)
        dl = self.joystick.get_button(13)
        dr = self.joystick.get_button(14)

        # Build message
        msg = {
            "lx": round(lx, 2),
            "ly": round(ly, 2),
            "rx": round(rx, 2),
            "ry": round(ry, 2),
            "L2": round(l2, 2),
            "R2": round(r2, 2),
            "a": a,
            "b": b,
            "x": x,
            "y": y,
            "L1": l1,
            "R1": r1,
            "du": du,
            "dd": dd,
            "dl": dl,
            "dr": dr,
        }

        self.label.setText(str(msg))

        # Send via TCP
        if self.sock:
            try:
                self.sock.sendall((str(msg) + "\n").encode())
            except Exception as e:
                print("TCP send failed:", e)
                self.sock.close()
                self.sock = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamepadWindow()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec())
