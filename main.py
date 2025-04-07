import sys
import os
import re
import tempfile
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QVBoxLayout, QFileDialog, QHBoxLayout, QFrame, QLabel,
                             QScrollArea, QMessageBox, QTextEdit, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

class LatexCompiler:
    def __init__(self, sections: dict):
        self.sections = sections

    def compile_to_pdf(self):
        temp_dir = tempfile.mkdtemp()
        tex_path = os.path.join(temp_dir, "document.tex")
        pdf_path = os.path.join(temp_dir, "document.pdf")

        try:
            tex_content = self.generate_latex()
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path],
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0 or not os.path.exists(pdf_path):
                return None, result.stdout, result.stderr

            return pdf_path, result.stdout, None

        except Exception as e:
            return None, None, str(e)

    def generate_latex(self):
        content = ""
        for title, lines in self.sections.items():
            section_text = "\n".join(lines)
            section_text = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', '[Image removed]', section_text)
            section_text = re.sub(r'\\definecolor\{[^}]+\}\{[^}]+\}\{[^}]+\}', '', section_text)
            section_text = re.sub(r'\\color\{[^}]+\}', '', section_text)
            section_text = re.sub(r'\\Needspace\{[^}]*\}', '', section_text)
            section_text = re.sub(r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1', section_text)
            section_text = re.sub(r'\\rowcolor\{[^}]+\}', '', section_text)
            section_text = re.sub(r'\\cellcolor\{[^}]+\}', '', section_text)
            section_text = re.sub(r'\\newpage', '', section_text)
            section_text = re.sub(r'\\newline\s*%', '', section_text)

            if section_text.count(r'\begin{longtable') > section_text.count(r'\end{longtable'):
                section_text += '\n\\end{longtable}'

            content += section_text + "\n\n"

        return rf"""
\documentclass[12pt]{{article}}
\usepackage{{amsmath, amssymb, longtable, multirow, geometry, array, tabularx}}
\usepackage[dvipsnames,table]{{xcolor}}
\usepackage{{graphicx, hyperref}}
\geometry{{a4paper, margin=1in}}

\title{{Auto-Generated LaTeX Document}}
\date{{}}

\begin{{document}}

{content}

\end{{document}}
"""

def collect_sections(filepath: str, end_word: str):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            capturing = False
            buffer = []
            mapped_data = {}

            for line in lines:
                if not capturing:
                    match = re.match(r'(\\section|\\subsection)\s*{(.*?)}', line)
                    if match:
                        capturing = True
                        title = match.group(2).strip()
                        buffer = [line.strip()]
                        continue

                if capturing:
                    if end_word in line:
                        buffer.append(line.strip())
                        capturing = False
                        mapped_data[title] = buffer
                        buffer = []
                        continue
                    buffer.append(line.strip())

            return mapped_data if mapped_data else None
    except Exception:
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX Section PDF Renderer")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.ui_stack = []
        self.show_import_screen()

    def show_error_dialog(self, title, message):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(message)
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec_()

    def clear_layout(self):
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_import_screen(self):
        self.clear_layout()
        self.ui_stack.append("import_screen")
        importButton = QPushButton('Import a .tex file')
        importButton.setFixedSize(200, 80)
        importButton.clicked.connect(self.on_import_button_click)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(importButton, 0, Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def on_import_button_click(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "LaTex Files (*.tex)")
        if filename:
            sections = collect_sections(filename, "\\end")
            if sections:
                self.show_section_selection_screen(filename, sections)
            else:
                QMessageBox.warning(self, "Extraction Failed", "Failed to extract sections.")

    def show_section_selection_screen(self, filename, sections):
        self.clear_layout()
        self.ui_stack.append("section_selection_screen")
        self.current_filename = filename
        self.current_sections = sections
        self.selected_sections = set()
        self.section_buttons = {}

        header_label = QLabel(f"Sections found in: {os.path.basename(filename)}")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        self.main_layout.addWidget(header_label)

        back_button = QPushButton('Back')
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.go_back)
        self.main_layout.addWidget(back_button)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        self.main_layout.addWidget(line)

        self.main_layout.addWidget(QLabel(f"Found {len(sections)} sections"))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for name in sections:
            section_container = QWidget()
            section_layout = QHBoxLayout(section_container)

            info_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold;")
            info_layout.addWidget(name_label)

            if len(sections[name]) > 1:
                preview = QLabel(sections[name][1][:60] + "...")
                preview.setStyleSheet("font-style: italic; color: gray;")
                info_layout.addWidget(preview)

            section_layout.addLayout(info_layout)

            button = QPushButton("Select")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, n=name: self.toggle_section(n, checked))
            section_layout.addWidget(button)

            self.section_buttons[name] = button
            scroll_layout.addWidget(section_container)

        scroll_area.setWidget(scroll_widget)
        self.main_layout.addWidget(scroll_area)

        extract_button = QPushButton("Generate PDF")
        extract_button.clicked.connect(self.extract_selected)
        self.main_layout.addWidget(extract_button)

    def toggle_section(self, name, checked):
        if checked:
            self.selected_sections.add(name)
            self.section_buttons[name].setStyleSheet("background-color: green; color: white;")
        else:
            self.selected_sections.discard(name)
            self.section_buttons[name].setStyleSheet("")

    def extract_selected(self):
        if not self.selected_sections:
            QMessageBox.warning(self, "No Selection", "Select at least one section.")
            return

        selected = {s: self.current_sections[s] for s in self.selected_sections}
        compiler = LatexCompiler(selected)
        pdf_path, out, err = compiler.compile_to_pdf()

        if pdf_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        else:
            error_msg = err or out or "Unknown error"
            self.show_error_dialog("Render Error", error_msg)

    def go_back(self):
        if len(self.ui_stack) > 1:
            self.ui_stack.pop()
            previous = self.ui_stack[-1]
            if previous == "import_screen":
                self.show_import_screen()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
