import sys
import pygame
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

        # --- Timer to poll gamepad ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_gamepad)
        self.timer.start(50)  # poll every 50ms

    def poll_gamepad(self):
        if not self.joystick:
            return

        pygame.event.pump()

        # --- Sticks ---
        lx = self.joystick.get_axis(0)
        ly = self.joystick.get_axis(1)
        rx = self.joystick.get_axis(2)
        ry = self.joystick.get_axis(3)

        # --- Triggers (L2, R2 are analog) ---
        l2 = self.joystick.get_axis(4)
        r2 = self.joystick.get_axis(5)

        # --- Buttons ---
        a = self.joystick.get_button(0)
        b = self.joystick.get_button(1)
        x = self.joystick.get_button(2)
        y = self.joystick.get_button(3)

        l1 = self.joystick.get_button(9)
        r1 = self.joystick.get_button(10)

        dup = self.joystick.get_button(11)
        ddown = self.joystick.get_button(12)
        dleft = self.joystick.get_button(13)
        dright = self.joystick.get_button(14)

        # --- Display all values ---
        self.label.setText(
            f"LStick=({lx:.2f},{ly:.2f}) RStick=({rx:.2f},{ry:.2f})\n"
            f"A={a} B={b} X={x} Y={y}\n"
            f"DUp={dup} DDown={ddown} DLeft={dleft} DRight={dright}\n"
            f"L1={l1} R1={r1}\n"
            f"L2={l2:.2f} R2={r2:.2f}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamepadWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec())
