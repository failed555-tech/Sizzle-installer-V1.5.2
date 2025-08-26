import sys, os, subprocess, ctypes

# --- Auto dependency installer ---
def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing dependency: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for package in ["PyQt6", "requests"]:
    ensure_package(package)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QTabWidget, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QColor
import requests

# ------------------------------
CATEGORIES = {
    "Music": [
        ("Song 1", "https://upload.wikimedia.org/wikipedia/commons/5/5c/Blue_Gradient_Background.jpg", "song1.mp3"),
        ("Song 2", "https://upload.wikimedia.org/wikipedia/commons/5/5c/Blue_Gradient_Background.jpg", "song2.mp3"),
    ],
    "Config": [
        ("Main Config", "https://upload.wikimedia.org/wikipedia/commons/5/5c/Blue_Gradient_Background.jpg", "config.ini"),
    ],
    "Scripts": [
        ("Setup Script", "https://upload.wikimedia.org/wikipedia/commons/5/5c/Blue_Gradient_Background.jpg", "setup.py"),
    ],
}
# ------------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_install_path():
    if os.name == "nt":
        if is_admin():
            path = r"C:\Program Files\FrutigerAeroInstaller"
        else:
            path = os.path.expanduser("~/Downloads/FrutigerAeroInstaller")
    else:
        path = os.path.expanduser("~/FrutigerAeroInstaller")
    os.makedirs(path, exist_ok=True)
    return path

def download_background(path):
    url = "https://upload.wikimedia.org/wikipedia/commons/5/5c/Blue_Gradient_Background.jpg"
    try:
        r = requests.get(url, stream=True, timeout=15)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"Background downloaded: {path}")
        return True
    except Exception as e:
        print(f"Failed to download background: {e}")
        return False

class InstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frutiger Aero Installer")
        self.setGeometry(150, 100, 800, 600)

        self.dest_folder = get_install_path()
        self.bg_path = os.path.join(self.dest_folder, "background.jpg")

        bg_ok = download_background(self.bg_path)

        # Apply background
        if bg_ok and os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path)
            palette = self.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)
        else:
            # fallback gradient
            self.setStyleSheet("QMainWindow { background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #66b3ff, stop:1 #3399ff); }")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)

        for cat, files in CATEGORIES.items():
            self.tabs.addTab(self.build_category_tab(cat, files), cat)

        self.install_all_btn = QPushButton("Install EVERYTHING")
        self.install_all_btn.clicked.connect(self.install_everything)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(140)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.tabs)
        layout.addWidget(self.install_all_btn)
        layout.addWidget(self.log_box)
        self.setCentralWidget(central)

        # Apply Aero-style panels/buttons
        self.setStyleSheet(self.aero_style())
        self.log(f"Installing into: {self.dest_folder}")

    def build_category_tab(self, category, files):
        page = QWidget()
        vbox = QVBoxLayout(page)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)

        for label, url, filename in files:
            btn = QPushButton(f"Install {label}")
            btn.clicked.connect(lambda _, u=url, f=filename, l=label: self.install_file(u, f, l))
            inner_layout.addWidget(btn)

        all_btn = QPushButton(f"Install All {category}")
        all_btn.clicked.connect(lambda _, fs=files: self.install_all(fs))
        inner_layout.addWidget(all_btn)

        inner.setLayout(inner_layout)
        scroll_area.setWidget(inner)
        vbox.addWidget(scroll_area)
        return page

    def install_file(self, url, filename, label):
        os.makedirs(self.dest_folder, exist_ok=True)
        dest_path = os.path.join(self.dest_folder, filename)

        if os.path.exists(dest_path):
            reply = QMessageBox.question(
                self, "File Exists",
                f"{label} already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.log(f"Skipped {label}")
                return

        try:
            self.log(f"Downloading {label}...")
            r = requests.get(url, stream=True, timeout=15)
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            self.log(f"Installed {label} → {dest_path}")
        except Exception as e:
            self.log(f"Failed {label}: {e}")

    def install_all(self, files):
        for label, url, filename in files:
            self.install_file(url, filename, label)

    def install_everything(self):
        self.log("Installing EVERYTHING...")
        for cat, files in CATEGORIES.items():
            self.install_all(files)
        self.log("All categories installed.")

    def log(self, text):
        self.log_box.append(text)

    def aero_style(self):
        # Semi-transparent panels and glossy buttons
        return f"""
        QTabWidget::pane {{
            background: rgba(255,255,255,120);
            border-radius: 16px;
            border: 2px solid rgba(255,255,255,200);
            padding: 8px;
        }}
        QTabBar::tab {{
            background: rgba(255,255,255,140);
            border-radius: 12px;
            padding: 10px 18px;
            margin: 4px;
            font-weight: bold;
            border: 1px solid rgba(255,255,255,180);
            color: black;
        }}
        QTabBar::tab:selected {{
            background: rgba(255,255,255,200);
            border: 2px solid white;
        }}
        QPushButton {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:0.3 #ccefff,
                stop:0.7 #66b3ff, stop:1 #3399ff
            );
            border-radius: 14px;
            padding: 8px 20px;
            border: 1px solid rgba(255,255,255,180);
            font-weight: bold;
            color: black;
        }}
        QPushButton:hover {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #99ccff
            );
        }}
        QTextEdit {{
            background: rgba(255,255,255,180);
            border: 1px solid rgba(255,255,255,200);
            border-radius: 12px;
            padding: 8px;
            font-size: 13px;
            color: #000;
        }}
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerApp()
    window.show()
    sys.exit(app.exec())
