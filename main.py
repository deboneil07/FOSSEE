import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog)
from PyQt5.QtCore import Qt

WINDOW_WIDTH=1024
WINDOW_HEIGHT=768

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Starter Template")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.ui_stack = []
        self.show_import_screen()

    # def initUI(self):
    #     # main menu state
    #     self.state1 = QWidget()
    #     layout1 = QVBoxLayout()
    #     importButtonX = int(WINDOW_WIDTH / 2) - 180
    #     importButtonY = int(WINDOW_HEIGHT / 2) - 100
    #     self.importButton = QPushButton('Import a file')
    #     self.importButton.setGeometry(importButtonX, importButtonY, 200, 80)
    #     self.importButton.clicked.connect(self.on_importButton_click)
    #
    #     layout1.addWidget(self.importButton)
    #     self.state1.setLayout(layout1)
    #
    #     self.central_widget.addWidget(self.state1)
    #     self.central_widget.setCurrentWidget(self.state1)

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_import_screen(self):
        self.clear_layout()
        self.ui_stack.append("import_screen")

        # Import button
        importButton = QPushButton('Import a file')
        importButton.setFixedSize(200, 80)
        importButton.clicked.connect(self.on_importButton_click)

        # Center the button
        self.layout.addStretch()
        self.layout.addWidget(importButton, 0, Qt.AlignCenter)
        self.layout.addStretch()

    def show_processing_screen(self, filename):
        self.clear_layout()
        self.ui_stack.append("processing_screen")

        # Back button
        backButton = QPushButton('Back')
        backButton.setFixedSize(200, 80)
        backButton.clicked.connect(self.go_back)

        # Some other button (example)
        processButton = QPushButton(f'Process {filename}')
        processButton.setFixedSize(200, 80)
        processButton.clicked.connect(lambda: print(f"Processing {filename}"))

        # Layout for buttons
        self.layout.addWidget(backButton)
        self.layout.addWidget(processButton)
        self.layout.addStretch()

    # def on_importButton_click(self):
    #     print("test clicked")

    def on_importButton_click(self):
        # Open file dialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if filename:
            print(f"File selected: {filename}")
            self.show_processing_screen(filename)

    def go_back(self):
        if len(self.ui_stack) > 1:
            self.ui_stack.pop()  # Remove current state
            previous_state = self.ui_stack[-1]  # Get previous state

            if previous_state == "import_screen":
                self.show_import_screen()
            # Add more states here if needed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
