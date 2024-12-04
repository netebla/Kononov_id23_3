import sys
import random
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel, QComboBox
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen


class RainDrop:
    def __init__(self, x: float, y: float, speed: float, angle: float, opacity: float):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.opacity = opacity
        self.width = random.uniform(3, 6)
        self.height = 30
        self.color = QColor("Lightblue")
        self.border_color = QColor("Blue")
        self.border_thickness = -4

    def fall(self):
        self.x += self.angle
        self.y += self.speed


class Cloud:
    def __init__(self, x: int, y: int, width: int, height: int, density: int, speed: float, shape: str = "rectangle"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.density = density
        self.speed = speed
        self.shape = shape
        self.selected = False

    def generate_drops(self) -> list[RainDrop]:
        drops = []
        for _ in range(self.density):
            drop_x = random.uniform(self.x, self.x + self.width)
            drop_y = self.y + self.height
            angle = random.uniform(-2, 2)
            opacity = random.uniform(0.5, 1.0)
            drops.append(RainDrop(drop_x, drop_y, self.speed, angle, opacity))
        return drops

    def contains(self, point: QPoint) -> bool:
        return self.x <= point.x() <= self.x + self.width and self.y <= point.y() <= self.y + self.height


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)
        self.clouds: list[Cloud] = []
        self.rains: list[RainDrop] = []
        self.selected_cloud = None
        self.dragging_cloud = None
        self.offset = QPoint(0, 0)

        self.init_ui()
        self.init_timers()

    def init_ui(self):
        control_panel = QWidget(self)
        control_panel.setGeometry(0, 0, 200, self.height())
        layout = QVBoxLayout()

        add_cloud_btn = QPushButton("Добавить тучку")
        add_cloud_btn.clicked.connect(self.add_cloud)
        layout.addWidget(add_cloud_btn)

        delete_cloud_btn = QPushButton("Удалить выбранную тучку")
        delete_cloud_btn.clicked.connect(self.delete_selected_cloud)
        layout.addWidget(delete_cloud_btn)

        self.density_slider = QSlider(Qt.Orientation.Horizontal)
        self.density_slider.setRange(1, 20)
        self.density_slider.setValue(10)
        self.density_slider.valueChanged.connect(self.update_cloud_density)
        layout.addWidget(QLabel("Плотность капель"))
        layout.addWidget(self.density_slider)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 30)
        self.speed_slider.setValue(15)
        self.speed_slider.valueChanged.connect(self.update_cloud_speed)
        layout.addWidget(QLabel("Скорость капель"))
        layout.addWidget(self.speed_slider)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(50, 300)
        self.size_slider.setValue(100)
        self.size_slider.valueChanged.connect(self.update_cloud_size)
        layout.addWidget(QLabel("Размер тучки"))
        layout.addWidget(self.size_slider)

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["rectangle", "ellipse", "pooh"])
        self.shape_combo.currentTextChanged.connect(self.update_cloud_shape)
        layout.addWidget(QLabel("Форма тучки"))
        layout.addWidget(self.shape_combo)

        control_panel.setLayout(layout)

    def init_timers(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_positions)
        self.update_timer.start(16)  # 60 FPS (16 ms)

    def add_cloud(self):
        self.clouds.append(Cloud(300, 200, 100, 50, 10, 15, "rectangle"))
        self.update()

    def delete_selected_cloud(self):
        if self.selected_cloud in self.clouds:
            self.clouds.remove(self.selected_cloud)
            self.selected_cloud = None
        self.update()

    def update_cloud_density(self):
        if self.selected_cloud:
            self.selected_cloud.density = self.density_slider.value()

    def update_cloud_speed(self):
        if self.selected_cloud:
            self.selected_cloud.speed = self.speed_slider.value()

    def update_cloud_shape(self):
        if self.selected_cloud:
            self.selected_cloud.shape = self.shape_combo.currentText()

    def update_cloud_size(self):
        if self.selected_cloud:
            self.selected_cloud.width = self.size_slider.value()
            self.selected_cloud.height = self.size_slider.value() // 2

    def update_positions(self):
        for cloud in self.clouds:
            self.rains.extend(cloud.generate_drops())
        for rain in self.rains:
            rain.fall()
        self.rains = [r for r in self.rains if r.y < self.height()]
        self.update()

    def mousePressEvent(self, event):
        for cloud in reversed(self.clouds):
            if cloud.contains(event.pos()):
                self.selected_cloud = cloud
                self.dragging_cloud = cloud
                self.offset = event.pos() - QPoint(cloud.x, cloud.y)

                self.density_slider.setValue(cloud.density)
                self.speed_slider.setValue(cloud.speed)
                self.shape_combo.setCurrentText(cloud.shape)
                self.size_slider.setValue(cloud.width)
                break

    def mouseMoveEvent(self, event):
        if self.dragging_cloud:
            self.dragging_cloud.x = event.pos().x() - self.offset.x()
            self.dragging_cloud.y = event.pos().y() - self.offset.y()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_cloud = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for cloud in self.clouds:
            painter.setBrush(QBrush(Qt.GlobalColor.gray if not cloud.selected else Qt.GlobalColor.yellow))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))

            if cloud.shape == "rectangle":
                painter.drawRect(cloud.x, cloud.y, cloud.width, cloud.height)
            elif cloud.shape == "ellipse":
                painter.drawEllipse(cloud.x, cloud.y, cloud.width, cloud.height)
            elif cloud.shape == "pooh":
                body_width = cloud.width
                body_height = int(cloud.height * 1.5)
                painter.drawEllipse(cloud.x, cloud.y + cloud.height // 4, body_width, body_height)

                head_diameter = int(cloud.width * 0.6)
                painter.drawEllipse(
                    cloud.x + (cloud.width - head_diameter) // 2,
                    cloud.y - head_diameter // 2,
                    head_diameter,
                    head_diameter,
                )

                ear_diameter = int(head_diameter * 0.3)
                painter.drawEllipse(
                    cloud.x + (cloud.width - head_diameter) // 2 - ear_diameter // 2,
                    cloud.y - head_diameter // 2,
                    ear_diameter,
                    ear_diameter,
                )
                painter.drawEllipse(
                    cloud.x + (cloud.width + head_diameter) // 2 - ear_diameter // 2,
                    cloud.y - head_diameter // 2,
                    ear_diameter,
                    ear_diameter,
                )

        for rain in self.rains:
            painter.setOpacity(rain.opacity)
            painter.setBrush(QBrush(rain.color))
            painter.setPen(QPen(rain.border_color, rain.border_thickness))
            painter.drawRect(int(rain.x - rain.width // 2), int(rain.y), int(rain.width), int(rain.height))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
