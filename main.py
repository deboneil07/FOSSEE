import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QStackedWidget

WINDOW_WIDTH=1024
WINDOW_HEIGHT=768

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Starter Template")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.initUI()

    def initUI(self):
        # main menu state
        self.state1 = QWidget()
        layout1 = QVBoxLayout()
        importButtonX = int(WINDOW_WIDTH / 2) - 180
        importButtonY = int(WINDOW_HEIGHT / 2) - 100
        self.importButton = QPushButton('Import a file')
        self.importButton.setGeometry(importButtonX, importButtonY, 200, 80)
        self.importButton.clicked.connect(self.on_importButton_click)

        layout1.addWidget(self.importButton)
        self.state1.setLayout(layout1)

        self.central_widget.addWidget(self.state1)
        self.central_widget.setCurrentWidget(self.state1)

    def on_importButton_click(self):
        print("test clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
