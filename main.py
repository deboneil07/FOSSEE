import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QWidget, QVBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768


def collect_data(filepath: str, start_word: str, end_word: str):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            capturing = False  # bool for tracing from /section, /subsection -> /end
            buffer = []
            mapped_data = {}
            map_id = 1

            for line in lines:
                if not capturing and start_word in line:
                    capturing = True
                    buffer = []  # reassigning buffer to empty on every iteration

                if capturing:
                    buffer.append(line.strip())  # removing newline chars

                    if end_word in line:
                        capturing = False
                        mapped_data[f"{map_id}"] = buffer
                        map_id += 1

            return mapped_data if mapped_data else None
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starter Template")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Stack to keep track of UI states
        self.ui_stack = []

        # Initial state
        self.show_import_screen()

    def clear_layout(self):
        # Remove all widgets from the layout
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
        importButton.clicked.connect(self.on_import_button_click)

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

    def on_import_button_click(self):
        # Open file dialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.tex)")

        if filename:
            print(f"File selected: {filename}")
            # WORK STALLED
            # self.show_processing_screen(filename)
            start_word = "\\section"
            end_word = "\\end"

            extracted_data = collect_data(filename, start_word, end_word)
            if extracted_data:
                print("content capturing success")
                for _, lines in extracted_data.items():
                    for line in lines:
                        print(line)
                    print()
            else:
                print("no matching content found :(")


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