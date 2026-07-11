import sys
import os
import glob
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QMessageBox, QSystemTrayIcon, QMenu,
    QScrollArea, QGridLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, QAction, QColor, QFont, QMouseEvent
from PySide6.QtCore import Qt, QPoint, QSize

from engine import set_wallpaper_window
from wallpaper import VideoWallpaper, WebWallpaper

# Constants
PAPERS_DIR = "papers"

# QSS for futuristic theme
STYLESHEET = """
QMainWindow {
    background-color: #0b0c10;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QWidget#scrollAreaWidgetContents {
    background-color: #0b0c10;
}
QLabel#title {
    color: #66fcf1;
    font-size: 24px;
    font-weight: bold;
    font-family: "Segoe UI";
    padding: 10px;
}
QLabel#subtitle {
    color: #c5c6c7;
    font-size: 14px;
    font-family: "Segoe UI";
    padding-bottom: 20px;
}
QPushButton#closeBtn {
    background-color: transparent;
    color: #c5c6c7;
    border: none;
    font-weight: bold;
    font-size: 16px;
}
QPushButton#closeBtn:hover {
    color: #ff4c4c;
}
QPushButton#stopBtn {
    background-color: #1f2833;
    color: #ff4c4c;
    border: 1px solid #ff4c4c;
    border-radius: 5px;
    padding: 10px;
    font-size: 14px;
    font-family: "Segoe UI";
}
QPushButton#stopBtn:hover {
    background-color: #ff4c4c;
    color: #0b0c10;
}
"""

class WallpaperCard(QWidget):
    def __init__(self, file_path, dashboard):
        super().__init__()
        self.file_path = file_path
        self.dashboard = dashboard
        self.setFixedSize(200, 150)
        self.setCursor(Qt.PointingHandCursor)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Name label
        filename = os.path.basename(file_path)
        self.name_label = QLabel(filename)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #45a29e; font-size: 14px; font-weight: bold; font-family: 'Segoe UI';")
        self.name_label.setWordWrap(True)
        self.layout.addWidget(self.name_label)

        # Type label
        ext = os.path.splitext(filename)[1].lower()
        type_str = "Video" if ext in ['.mp4', '.webm'] else "Web"
        self.type_label = QLabel(type_str)
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setStyleSheet("color: #c5c6c7; font-size: 12px; font-family: 'Segoe UI';")
        self.layout.addWidget(self.type_label)

        # Base style
        self.setStyleSheet("""
            WallpaperCard {
                background-color: #1f2833;
                border-radius: 10px;
                border: 2px solid #1f2833;
            }
            WallpaperCard:hover {
                border: 2px solid #66fcf1;
                background-color: #2c3846;
            }
        """)

        # Glow effect
        self.glow = QGraphicsDropShadowEffect(self)
        self.glow.setBlurRadius(20)
        self.glow.setColor(QColor("#66fcf1"))
        self.glow.setOffset(0, 0)
        self.glow.setEnabled(False)
        self.setGraphicsEffect(self.glow)

    def enterEvent(self, event):
        self.glow.setEnabled(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.glow.setEnabled(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dashboard.apply_wallpaper(self.file_path)
        super().mousePressEvent(event)


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        
        self.title = QLabel("Homepaper")
        self.title.setStyleSheet("color: #66fcf1; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px;")
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.parent.hide) # Hide to tray instead of exit
        
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.close_btn)
        
        self.setStyleSheet("background-color: #0b0c10;")
        self.setFixedHeight(40)
        
        self._is_dragging = False
        self._drag_pos = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            self.parent.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging = False
        event.accept()


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Homepaper")
        self.resize(750, 550)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        self.setStyleSheet(STYLESHEET)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(self.content_widget)
        
        # Header
        self.header = QLabel("Your Papers")
        self.header.setObjectName("title")
        self.content_layout.addWidget(self.header)
        
        self.subtitle = QLabel("Drop .mp4, .webm, or .html files into the 'papers' folder to see them here.")
        self.subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(self.subtitle)
        
        # Scroll Area for Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollAreaWidgetContents")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.content_layout.addWidget(self.scroll_area)
        
        # Controls
        self.controls_layout = QHBoxLayout()
        self.status_label = QLabel("No wallpaper applied.")
        self.status_label.setStyleSheet("color: #45a29e; font-family: 'Segoe UI';")
        self.btn_stop = QPushButton("Stop Wallpaper")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.clicked.connect(self.stop_wallpaper)
        self.btn_stop.setFixedWidth(150)
        
        self.controls_layout.addWidget(self.status_label)
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.btn_stop)
        self.content_layout.addLayout(self.controls_layout)
        
        self.current_wallpaper = None
        
        # Initialize folders and scan
        if not os.path.exists(PAPERS_DIR):
            os.makedirs(PAPERS_DIR)
        self.load_papers()

    def load_papers(self):
        # Clear existing
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Scan folder
        patterns = ["*.mp4", "*.webm", "*.html"]
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(PAPERS_DIR, pattern)))
        
        # Populate grid (3 columns)
        row, col = 0, 0
        for f in files:
            card = WallpaperCard(f, self)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def apply_wallpaper(self, path):
        self.stop_wallpaper()
        
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.mp4', '.webm']:
            self.current_wallpaper = VideoWallpaper(path)
            self.current_wallpaper.play()
        elif ext == '.html':
            self.current_wallpaper = WebWallpaper(path)
        else:
            return
            
        self._embed_wallpaper()
        self.status_label.setText(f"Playing: {os.path.basename(path)}")

    def _embed_wallpaper(self):
        if not self.current_wallpaper:
            return
            
        self.current_wallpaper.showFullScreen()
        hwnd = int(self.current_wallpaper.winId())
        
        if not set_wallpaper_window(hwnd):
            QMessageBox.critical(self, "Error", "Failed to embed wallpaper to the desktop background.")
            self.stop_wallpaper()

    def stop_wallpaper(self):
        if self.current_wallpaper:
            self.current_wallpaper.stop()
            self.current_wallpaper.close()
            self.current_wallpaper.deleteLater()
            self.current_wallpaper = None
            self.status_label.setText("No wallpaper applied.")

def main():
    app = QApplication(sys.argv if hasattr(sys, 'argv') else [])
    app.setWindowIcon(QIcon("icon.svg"))
    
    # Tray icon
    tray_icon = QSystemTrayIcon(QIcon("icon.svg"), app) 
    menu = QMenu()
    
    show_action = QAction("Show Dashboard")
    quit_action = QAction("Quit")
    
    menu.addAction(show_action)
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    
    dashboard = Dashboard()
    
    show_action.triggered.connect(dashboard.showNormal)
    quit_action.triggered.connect(app.quit)
    
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
