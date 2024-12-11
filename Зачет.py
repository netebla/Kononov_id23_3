import sys
import math
import random
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpinBox, QSlider, QLabel
)
from PyQt6.QtGui import QBrush, QColor

G = 9.81

class FountainSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fountain Simulation")
        self.resize(1200, 800)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.scene = QGraphicsScene(0, 0, 1200, 800)
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        control_layout = QHBoxLayout()

        self.stream_count_label = QLabel("Количество струй:")
        self.stream_count_spin = QSpinBox()
        self.stream_count_spin.setRange(1, 50)
        self.stream_count_spin.setValue(10)

        self.density_label = QLabel("Плотность воды:")
        self.density_spin = QSpinBox()
        self.density_spin.setRange(1, 1000)
        self.density_spin.setValue(1000)

        self.pressure_label = QLabel("Давление воды:")
        self.pressure_slider = QSlider(Qt.Orientation.Horizontal)
        self.pressure_slider.setRange(1, 100)
        self.pressure_slider.setValue(50)

        self.angle_label = QLabel("Угол наклона:")
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(0, 90)
        self.angle_slider.setValue(45)

        self.start_button = QPushButton("Запуск анимации")
        self.reset_button = QPushButton("Сброс")

        control_layout.addWidget(self.stream_count_label)
        control_layout.addWidget(self.stream_count_spin)
        control_layout.addWidget(self.density_label)
        control_layout.addWidget(self.density_spin)
        control_layout.addWidget(self.pressure_label)
        control_layout.addWidget(self.pressure_slider)
        control_layout.addWidget(self.angle_label)
        control_layout.addWidget(self.angle_slider)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.reset_button)

        layout.addLayout(control_layout)

        self.start_button.clicked.connect(self.start_animation)
        self.reset_button.clicked.connect(self.reset_animation)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        self.stream_timer = QTimer()
        self.stream_timer.timeout.connect(self.create_streams)

        self.droplets = []

    def start_animation(self):
        self.reset_animation()
        self.timer.start(30)
        self.stream_timer.start(100)

    def reset_animation(self):
        self.timer.stop()
        self.stream_timer.stop()
        self.scene.clear()
        self.droplets.clear()

    def create_streams(self):
        n = self.stream_count_spin.value()
        pressure = self.pressure_slider.value()
        density = self.density_spin.value()
        angle_deg = self.angle_slider.value()

        v0 = math.sqrt(2 * pressure / density)

        start_x_min = 600 - n * 5
        start_x_max = 600 + n * 5

        for _ in range(n):
            start_x = random.randint(start_x_min, start_x_max)
            start_y = 600

            angle = math.radians(angle_deg + random.uniform(-5, 5))

            droplet = {
                "item": QGraphicsEllipseItem(0, 0, 5, 5),
                "v0": v0,
                "angle": angle,
                "time": 0,
                "start_pos": QPointF(start_x, start_y)
            }
            droplet["item"].setBrush(QBrush(QColor("blue")))
            droplet["item"].setPos(start_x, start_y)
            self.scene.addItem(droplet["item"])
            self.droplets.append(droplet)

    def update_animation(self):
        dt = 0.05
        for droplet in self.droplets[:]:
            droplet["time"] += dt
            v0 = droplet["v0"]
            angle = droplet["angle"]
            t = droplet["time"]

            x = droplet["start_pos"].x() + v0 * math.cos(angle) * t
            y = droplet["start_pos"].y() - (v0 * math.sin(angle) * t - 0.5 * G * t ** 2)

            droplet["item"].setPos(x, y)

            if y > 800 or x > 1200 or x < 0:
                self.scene.removeItem(droplet["item"])
                self.droplets.remove(droplet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FountainSimulation()
    window.show()
    sys.exit(app.exec())