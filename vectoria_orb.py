
import math
import queue
import threading
import sys

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QRadialGradient,
    QLinearGradient,
    QPainterPath,
)
from PySide6.QtWidgets import QApplication, QWidget, QMenu


orb_clicked = threading.Event()


class VectoriaOrb(QWidget):
    VALID_STATES = {"idle", "listening", "thinking", "speaking"}

    def __init__(self):
        super().__init__()

        self.orb_size = 112
        self.phase = 0.0
        self.state = "idle"
        self.state_queue = queue.Queue()

        self.drag_position = QPoint()
        self.is_dragging = False
        self.drag_threshold = 10

        self.setWindowTitle("Vectoria")
        self.setToolTip("Vectoria — click to activate")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )

        self.setFixedSize(self.orb_size, self.orb_size)

        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.move(
                geometry.right() - self.width() - 24,
                geometry.bottom() - self.height() - 48,
            )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    # Safe to call from the voice-assistant thread.
    def set_state(self, state):
        if state in self.VALID_STATES:
            self.state_queue.put(state)

    def _apply_state(self, state):
        self.state = state

        tooltips = {
            "idle": "Vectoria — ready",
            "listening": "Vectoria — listening",
            "thinking": "Vectoria — thinking",
            "speaking": "Vectoria — speaking",
        }

        self.setToolTip(tooltips[state])

    def animate(self):
        latest_state = None
        while True:
            try:
                latest_state = self.state_queue.get_nowait()
            except queue.Empty:
                break

        if latest_state is not None:
            self._apply_state(latest_state)

        # Each state gets a clearly different movement rhythm.
        speed = {
            "idle": 0.045,
            "listening": 0.105,
            "thinking": 0.145,
            "speaking": 0.19,
        }[self.state]
        self.phase = (self.phase + speed) % (2 * math.pi * 100)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        phase = self.phase

        pulse_rate = {
            "idle": 0.75,
            "listening": 1.65,
            "thinking": 1.15,
            "speaking": 2.15,
        }[self.state]
        pulse = (math.sin(phase * pulse_rate) + 1) / 2
        breathe = (math.sin(phase * 0.72) + 1) / 2

        core_radius = {
            "idle": 18.5 + breathe * 2.0,
            "listening": 18.0 + pulse * 5.0,
            "thinking": 19.0 + pulse * 3.8,
            "speaking": 18.0 + pulse * 6.0,
        }[self.state]

        # 2. Translucent glass shell with subtle depth.
        shell_radius = 34 + breathe * 1.0

        shell = QRadialGradient(
            cx - 12, cy - 15, shell_radius * 1.9
        )
        shell.setColorAt(0.0, QColor(255, 255, 255, 8))
        shell.setColorAt(0.48, QColor(255, 225, 180, 10))
        shell.setColorAt(0.76, QColor(255, 194, 112, 22))
        shell.setColorAt(0.91, QColor(255, 218, 164, 48))
        shell.setColorAt(1.0, QColor(255, 236, 203, 75))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shell)
        painter.drawEllipse(
            int(cx - shell_radius),
            int(cy - shell_radius),
            int(shell_radius * 2),
            int(shell_radius * 2),
        )



        # 3. State-aware core: translucent glass when idle.
        core = QRadialGradient(
            cx - 5, cy - 7, core_radius * 1.8
        )

        if self.state == "idle":
            core.setColorAt(0.0, QColor(255, 244, 207, 235))
            core.setColorAt(0.25, QColor(255, 203, 112, 235))
            core.setColorAt(0.55, QColor(255, 160, 48, 220))
            core.setColorAt(0.82, QColor(235, 119, 27, 155))
            core.setColorAt(1.0, QColor(255, 145, 36, 0))

        else:
            core.setColorAt(0.0, QColor(255, 255, 229, 255))
            core.setColorAt(0.18, QColor(255, 226, 151, 255))
            core.setColorAt(0.48, QColor(255, 173, 51, 245))
            core.setColorAt(0.78, QColor(229, 111, 20, 170))
            core.setColorAt(1.0, QColor(255, 145, 36, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(core)
        painter.drawEllipse(
            int(cx - core_radius * 1.8),
            int(cy - core_radius * 1.8),
            int(core_radius * 3.6),
            int(core_radius * 3.6),
        )

        # Clip the fluid light to the core so it appears inside the glass.
        clip_path = QPainterPath()
        clip_path.addEllipse(
            cx - core_radius * 1.15, cy - core_radius * 1.15,
            core_radius * 2.3, core_radius * 2.3,
        )
        painter.save()
        painter.setClipPath(clip_path)

        if self.state == "idle":
            colors = [(255, 250, 225, 125), (255, 219, 160, 95)]
            count, travel, patch_scale, motion_speed = 2, 5.0, 1.0, 0.52
        elif self.state == "listening":
            colors = [
                (255, 255, 235, 200),
                (255, 237, 195, 165),
                (210, 241, 255, 115),
            ]
            count, travel, patch_scale, motion_speed = 3, 10.0, 1.18, 1.15
        elif self.state == "thinking":
            colors = [
                (255, 244, 211, 190),
                (255, 185, 92, 180),
                (255, 224, 172, 155),
                (255, 252, 228, 135),
            ]
            count, travel, patch_scale, motion_speed = 4, 11.0, 1.10, 1.45
        else:  # speaking
            colors = [
                (255, 255, 230, 225),
                (255, 205, 150, 205),
                (255, 166, 105, 180),
                (255, 228, 180, 170),
            ]
            count, travel, patch_scale, motion_speed = 4, 12.0, 1.25, 1.85

        for i in range(count):
            red, green, blue, base_alpha = colors[i]
            angle = phase * motion_speed + i * (2.0 * math.pi / count)

            if self.state == "thinking":
                # Directional swirl, visibly different from the other states.
                x = cx + math.cos(angle) * travel
                y = cy + math.sin(angle * 1.35) * travel * 0.78
            elif self.state == "speaking":
                # Faster irregular flow, with stronger pulsing.
                x = cx + math.sin(angle * 0.92 + i) * travel
                y = cy + math.cos(angle * 1.18 + i * 1.3) * travel * 0.82
            elif self.state == "listening":
                spread = 0.45 + pulse * 0.75
                x = cx + math.sin(angle + i) * travel * spread
                y = cy + math.cos(angle * 0.8 + i) * travel * spread
            else:
                x = cx + math.sin(angle * 0.8 + i) * travel
                y = cy + math.cos(angle * 0.7 + i * 1.4) * travel * 0.7

            radius = (10.5 + pulse * 3.0 + (i % 2) * 1.5) * patch_scale
            alpha = min(255, int(base_alpha * (0.72 + pulse * 0.28)))
            light = QRadialGradient(x - radius * 0.25, y - radius * 0.3, radius * 1.5)
            light.setColorAt(0.0, QColor(red, green, blue, alpha))
            light.setColorAt(0.42, QColor(red, green, blue, int(alpha * 0.62)))
            light.setColorAt(1.0, QColor(red, green, blue, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(light)
            painter.drawEllipse(
                int(x - radius), int(y - radius),
                int(radius * 2), int(radius * 2),
            )

        painter.restore()

    # ------------------------------------------------------
    # WINDOW INTERACTION
    # ------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            self.is_dragging = False
            event.accept()

        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(
                event.globalPosition().toPoint()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_position = (
                event.globalPosition().toPoint()
                - self.drag_position
            )

            if (
                current_position - self.pos()
            ).manhattanLength() >= self.drag_threshold:
                self.is_dragging = True

            if self.is_dragging:
                self.move(current_position)

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_dragging:
                orb_clicked.set()

            self.is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        states = [
            "idle",
            "listening",
            "thinking",
            "speaking",
        ]

        next_index = (
            states.index(self.state) + 1
        ) % len(states)

        self.set_state(states[next_index])
        event.accept()

    def show_context_menu(self, position):
        menu = QMenu(self)

        idle_action = menu.addAction("Demo: Idle")
        listening_action = menu.addAction("Demo: Listening")
        thinking_action = menu.addAction("Demo: Thinking")
        speaking_action = menu.addAction("Demo: Speaking")

        menu.addSeparator()
        exit_action = menu.addAction("Exit Orb")

        selected = menu.exec(position)

        if selected == idle_action:
            self.set_state("idle")
        elif selected == listening_action:
            self.set_state("listening")
        elif selected == thinking_action:
            self.set_state("thinking")
        elif selected == speaking_action:
            self.set_state("speaking")
        elif selected == exit_action:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    orb = VectoriaOrb()
    orb.show()

    sys.exit(app.exec())
