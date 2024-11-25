import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFrame, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QPalette, QIcon
import math
from typing import List, Tuple
from itertools import permutations

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1C1C1C"))
        self.setPalette(palette)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 5, 0)
        
        self.title_label = QLabel("Ypuf's Treasure Chest Path Finder")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        
        btn_layout = QHBoxLayout()
        
        self.minimize_button = QPushButton("─")
        self.minimize_button.setFixedSize(30, 25)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #1C1C1C;
                color: white;
                border: none;
                font-family: Arial;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 25)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #1C1C1C;
                color: #FF5C5C;
                border: none;
                font-family: Arial;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        
        btn_layout.addWidget(self.minimize_button)
        btn_layout.addWidget(self.close_button)
        btn_layout.setSpacing(2)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.start = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.start is not None:
            delta = event.pos() - self.start
            self.window().move(self.window().pos() + delta)

    def mouseReleaseEvent(self, event):
        self.start = None

class VisualizationWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QFrame {
                background-color: #2C2C2C;
                border: none;
                border-radius: 4px;
            }
        """)
        self.start_point = None
        self.coordinates = []
        self.current_path = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.start_point:
            self.draw_point(painter, self.start_point[0], self.start_point[1], QColor("#ff6b6b"))
        for x, y in self.coordinates:
            self.draw_point(painter, x, y, QColor("#4dabf7"))
        if self.current_path:
            self.draw_path(painter, self.current_path)

    def draw_point(self, painter: QPainter, x: float, y: float, color: QColor):
        canvas_x, canvas_y = self.scale_to_canvas(x, y)
        painter.setPen(QPen(color, 2))
        painter.setBrush(color)
        painter.drawEllipse(int(canvas_x-4), int(canvas_y-4), 8, 8)
        painter.setPen(QPen(QColor("#E0E0E0"), 1))
        painter.drawText(int(canvas_x+10), int(canvas_y-10), f"({x}, {y})")

    def draw_path(self, painter: QPainter, path: List[Tuple[float, float]]):
        if not path:
            return
        painter.setPen(QPen(QColor("#3A9AD9"), 2))
        for i in range(len(path) - 1):
            x1, y1 = self.scale_to_canvas(path[i][0], path[i][1])
            x2, y2 = self.scale_to_canvas(path[i + 1][0], path[i + 1][1])
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def scale_to_canvas(self, x: float, y: float) -> Tuple[float, float]:
        all_points = [self.start_point] + self.coordinates if self.start_point else self.coordinates
        
        if not all_points:
            width = self.width()
            height = self.height()
            return width/2 + x, height/2 - y
            
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        padding = 0.1
        x_range = max_x - min_x
        y_range = max_y - min_y
        
        if x_range == 0: x_range = 1
        if y_range == 0: y_range = 1
            
        min_x -= x_range * padding
        max_x += x_range * padding
        min_y -= y_range * padding
        max_y += y_range * padding
        
        canvas_width = self.width()
        canvas_height = self.height()
        canvas_padding = 20
        
        usable_width = canvas_width - 2 * canvas_padding
        usable_height = canvas_height - 2 * canvas_padding
        
        scale_x = usable_width / (max_x - min_x)
        scale_y = usable_height / (max_y - min_y)
        scale = min(scale_x, scale_y)
        
        x_offset = canvas_padding + (usable_width - (max_x - min_x) * scale) / 2
        y_offset = canvas_padding + (usable_height - (max_y - min_y) * scale) / 2
        
        canvas_x = x_offset + (x - min_x) * scale
        canvas_y = canvas_height - (y_offset + (y - min_y) * scale)
        
        return canvas_x, canvas_y

    def update_visualization(self, start_point=None, coordinates=None, path=None):
        if start_point is not None:
            self.start_point = start_point
        if coordinates is not None:
            self.coordinates = coordinates
        if path is not None:
            self.current_path = path
        self.update()

class PathFinderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(800, 800)
        self.setWindowTitle("Ypuf's Treasure Chest Path Finder")
        self.setWindowIcon(QIcon("icon.ico"))
        
        container = QWidget()
        container.setObjectName("container")
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar()
        self.title_bar.setObjectName("titleBar")
        main_layout.addWidget(self.title_bar)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.close_button.clicked.connect(self.close)
        
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        
        input_frame = QWidget()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        x_label = QLabel("X:")
        x_label.setStyleSheet("color: #E0E0E0;")
        self.x_entry = QLineEdit()
        self.x_entry.setFixedWidth(80)
        
        z_label = QLabel("Z:")
        z_label.setStyleSheet("color: #E0E0E0;")
        self.y_entry = QLineEdit()
        self.y_entry.setFixedWidth(80)
        
        self.set_start_btn = QPushButton("Set Start Point") 
        add_point_btn = QPushButton("Add Point")
        
        input_layout.addWidget(x_label)
        input_layout.addWidget(self.x_entry)
        input_layout.addWidget(z_label)
        input_layout.addWidget(self.y_entry)
        input_layout.addWidget(self.set_start_btn)
        input_layout.addWidget(add_point_btn)
        input_layout.addStretch()
        
        viz_container = QWidget()
        viz_layout = QVBoxLayout(viz_container)
        viz_layout.setContentsMargins(0, 0, 0, 0)
        viz_layout.setSpacing(10)
        
        self.visualization = VisualizationWidget()
        viz_layout.addWidget(self.visualization)
        
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        calc_path_btn = QPushButton("Calculate Path")
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        
        button_layout.addWidget(calc_path_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        viz_layout.addWidget(button_frame)
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(500)
        
        content_layout.addWidget(input_frame)
        content_layout.addWidget(viz_container)
        content_layout.addWidget(self.result_text)
        
        main_layout.addWidget(content)
        
        self.set_start_btn.clicked.connect(self.add_start_point)
        add_point_btn.clicked.connect(self.add_point)
        calc_path_btn.clicked.connect(self.calculate_path)
        clear_btn.clicked.connect(self.clear_all)
        
        container.setStyleSheet("""
            QWidget#container {
                background-color: #121212;
                border-radius: 10px;
                border: 1px solid #121212;
            }
            QWidget#titleBar {
                background-color: #1C1C1C;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QWidget#content {
                background-color: #121212;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLineEdit {
                background-color: #2C2C2C;
                color: white;
                padding: 5px;
                border-radius: 4px;
                border: none;
            }
            QPushButton {
                background-color: #3A9AD9;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2D7AA9;
            }
            QTextEdit {
                background-color: #2C2C2C;
                color: white;
                padding: 5px;
                border-radius: 4px;
                border: none;
            }
        """)
        
        self.start_point = None
        self.coordinates = []

    def add_start_point(self):
        try:
            x = float(self.x_entry.text())
            y = float(self.y_entry.text())
            self.start_point = (x, y)
            self.visualization.update_visualization(start_point=self.start_point)
            self.x_entry.clear()
            self.y_entry.clear()
            self.set_start_btn.hide() 
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter valid numbers for coordinates")

    def clear_all(self):
        self.start_point = None
        self.coordinates = []
        
        self.visualization.start_point = None  
        self.visualization.coordinates = []
        self.visualization.current_path = None 
        self.visualization.update()
        
        self.x_entry.clear()
        self.y_entry.clear()
        self.result_text.clear()
        
        self.set_start_btn.show()

    def add_point(self):
        try:
            x = float(self.x_entry.text())
            y = float(self.y_entry.text())
            self.coordinates.append((x, y))
            self.visualization.update_visualization(coordinates=self.coordinates)
            self.x_entry.clear()
            self.y_entry.clear()
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter valid numbers for coordinates")

    def find_optimal_path(self, start: Tuple[float, float], points: List[Tuple[float, float]]) -> Tuple[List[Tuple[float, float]], float]:
        def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        if len(points) <= 3:
            best_path = None
            min_distance = float('inf')
            for perm in permutations(points):
                current_distance = distance(start, perm[0])
                for i in range(len(perm) - 1):
                    current_distance += distance(perm[i], perm[i + 1])
                if current_distance < min_distance:
                    min_distance = current_distance
                    best_path = [start] + list(perm)
            return best_path, min_distance

        def two_opt_swap(route: List[Tuple[float, float]], i: int, k: int) -> List[Tuple[float, float]]:
            return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

        def calculate_total_distance(route: List[Tuple[float, float]]) -> float:
            return sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))

        unvisited = points[:]
        path = [start]
        current = start
        while unvisited:
            nearest = min(unvisited, key=lambda p: distance(current, p))
            path.append(nearest)
            current = nearest
            unvisited.remove(nearest)

        improved = True
        while improved:
            improved = False
            best_distance = calculate_total_distance(path)
            for i in range(1, len(path) - 2):
                for k in range(i + 1, len(path)):
                    new_path = two_opt_swap(path, i, k)
                    new_distance = calculate_total_distance(new_path)
                    if new_distance < best_distance:
                        path = new_path
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break

        return path, calculate_total_distance(path)

    def calculate_path(self):
        if not self.start_point:
            msg = QMessageBox(self)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #121212;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #3A9AD9;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    border: none;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2D7AA9;
                }
            """)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Please set a start point first")
            msg.exec()
            return
            
        if not self.coordinates:
            msg = QMessageBox(self)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #121212;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #3A9AD9;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    border: none;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2D7AA9;
                }
            """)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Please add at least one point")
            msg.exec()
            return
            
        path, total_distance = self.find_optimal_path(self.start_point, self.coordinates)
        self.visualization.update_visualization(path=path)
        
        self.result_text.clear()
        self.result_text.append(f"Total distance: {total_distance:.2f} units\n\nOptimal Path:")
        for i, point in enumerate(path):
            self.result_text.append(f"{i}. ({point[0]}, {point[1]})")

def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: transparent;
        }
        QToolTip {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #3A9AD9;
            border-radius: 4px;
            padding: 4px;
        }
        QMessageBox {
            background-color: #121212;
            color: white;
        }
        QMessageBox QLabel {
            color: white;
        }
        QMessageBox QPushButton {
            background-color: #3A9AD9;
            color: white;
            padding: 5px 15px;
            border-radius: 4px;
            border: none;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #2D7AA9;
        }
    """)
    
    window = PathFinderGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()