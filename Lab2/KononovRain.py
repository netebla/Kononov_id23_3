import sys
import random
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import json

class RainDrop:
    def __init__(self, x, y):
        self.width = random.uniform(3, 6)
        self.x = x
        self.y = y
        self.height = 30
        self.opacity = random.uniform(0.5, 1.0)
        self.color = QColor("Lightblue")
        self.border_color = QColor("Blue")       # Цвет границы
        self.border_thickness = -4

    def fall(self, speed_min, speed_max, angle_min, angle_max):
        self.x += random.uniform(angle_min, angle_max)
        self.y += random.uniform(speed_min, speed_max)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)

        self.load_config()

        self.rains = []

        # Таймеры
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_rains_pads_position)
        self.update_timer.start(1)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_rains_pads)
        self.schedule_next_spawn()

    def load_config(self):
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                self.fall_speed_min = config["fall_speed_min"]
                self.fall_speed_max = config["fall_speed_max"]
                self.max_rains = config["max_rains"]
                self.angle_min = config["angle_min"]
                self.angle_max = config["angle_max"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            self.fall_speed_min = 10
            self.fall_speed_max = 15
            self.max_rains = 20
            self.angle_min = -2
            self.angle_max = 2

    def schedule_next_spawn(self):
        random_interval = random.randint(0, 5)
        self.spawn_timer.start(random_interval)

    def update_rains_pads_position(self):
        for rain in self.rains:
            rain.fall(self.fall_speed_min, self.fall_speed_max, self.angle_min, self.angle_max)

        self.rains = [rain for rain in self.rains if rain.y < self.height()]

        self.update()
        print(len(self.rains))

    def spawn_rains_pads(self):
        number_of_rains = random.randint(1, self.max_rains)

        for _ in range(number_of_rains):
            x = random.randint(0, self.width())
            y = 0
            rain = RainDrop(x, y)
            self.rains.append(rain)

        self.schedule_next_spawn()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for rain in self.rains:
            painter.setOpacity(rain.opacity)
            painter.setBrush(QBrush(rain.color))
            painter.setPen(QPen(rain.border_color, rain.border_thickness))
            painter.drawRect(int(rain.x - rain.width // 2), int(rain.y), int(rain.width), int(rain.height))  # Рисуем прямоугольную каплю

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
