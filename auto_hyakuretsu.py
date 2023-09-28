import importlib
import os
import random
import sys
import time

import pyautogui  # Import pyautogui for mouse control
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget, QVBoxLayout, QCheckBox

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import search_macros, Macro
from libs.sprite import load_sprites
from ui.mainWindow import Ui_MainWindow


class AutoHyakuretsu(QMainWindow, Ui_MainWindow):
    macros: list[Macro] = []
    sprites: dict = {}

    def __init__(self):
        super().__init__()
        self.timer = None
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.macros_dir = self.script_directory + "/macros"
        self.sounds_dir = self.script_directory + "/sounds"
        self.macros = []
        self.running = False
        self.timer_interval = 10
        self.loop_rate = 5000
        self.loop_countdown = 0
        self.sound = False
        self.lol = False
        self.ui_form = Ui_MainWindow()
        self.init_ui()
        self.update_ui_from_model()
        self.load_data()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        form = self.ui_form

        form.setupUi(self)
        form.soundCheckbox.stateChanged.connect(self.update_model_from_ui)
        form.lolCheckbox.stateChanged.connect(self.update_model_from_ui)
        form.toggleButton.clicked.connect(self.toggle_action)
        form.pollCountdown.setMinimum(0)
        form.pollRate.textChanged.connect(self.update_model_from_ui)

        table = form.macrosTable
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["active", "Module", "Macro", "run_nr"])
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 300)
        table.setColumnWidth(3, 150)

        table.setSortingEnabled(True)
        table.sortByColumn(0, Qt.AscendingOrder)  # Sort column 0 in ascending order

        # main loop timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_action)
        self.timer.start(self.timer_interval)

        self.refresh_ui()

    def load_data(self):
        self.sprites = load_sprites(self.script_directory + "/sprites", self.sounds_dir)

        macros = search_macros(self.macros_dir)

        table = self.ui_form.macrosTable
        table.setRowCount(len(macros))

        self.macros = []

        row = 0
        for macro in macros:
            checkbox_widget = CheckBoxCellWidget()
            table.setCellWidget(row, 0, checkbox_widget)

            module_name = macro["module"].replace(self.macros_dir + os.path.sep, "")
            table.setItem(row, 1, QTableWidgetItem(module_name))
            table.setItem(row, 2, QTableWidgetItem(macro["name"]))
            table.setItem(row, 3, QTableWidgetItem(str(macro["run_count"] if "run_count" in macro else 0)))

            macro_name = macro['name']
            spec = importlib.util.spec_from_file_location(macro_name, os.path.join(macro['module'], macro_name + ".py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Instantiate the class
            if hasattr(module, macro_name):
                class_ = getattr(module, macro_name)
                instance = class_(self, macro_name, os.path.join(self.macros_dir, module_name, 'templates'))
                print(f"Instantiated {macro_name}: {instance.name}")
                self.macros.append(instance)

            row += 1

    def update_model_from_ui(self):
        self.loop_rate = int(self.ui_form.pollRate.text())
        self.sound = self.ui_form.soundCheckbox.isChecked()
        self.lol = self.ui_form.lolCheckbox.isChecked()
        self.refresh_ui()

    def update_ui_from_model(self):
        self.ui_form.pollRate.setValue(self.loop_rate)
        self.ui_form.soundCheckbox.setChecked(self.sound)
        self.ui_form.lolCheckbox.setChecked(self.lol)
        self.refresh_ui()

    def toggle_action(self):
        self.running = not self.running
        self.refresh_ui()
        print("Starting" if self.running else "Stopping")

    def refresh_ui(self):
        # set the label of the button according to running status
        self.ui_form.toggleButton.setText("Stop" if self.running else "Start")
        # set the progress bar to the next poll
        self.ui_form.pollCountdown.setMaximum(self.loop_rate)
        self.ui_form.pollCountdown.setValue(self.loop_countdown)

    def timer_action(self):
        if not self.running:
            return

        if self.loop_countdown <= 0:
            self.loop_countdown = self.loop_rate
            print(f"Loop triggered at {time.strftime('%H:%M:%S', time.localtime())}")

            selected_rows = self.get_selected_macro_rows()
            if len(selected_rows) > 0:
                screenshot_cv = capture_screen()

                for row in selected_rows:
                    macro = self.macros[row]
                    print(f"Running macro {macro.name}")
                    macro.run(screenshot_cv)

        self.loop_countdown -= self.timer_interval
        self.refresh_ui()

    def click(self, x, y):
        mouse_x, mouse_y = pyautogui.position()
        pyautogui.click(x, y)
        pyautogui.moveTo(mouse_x, mouse_y)

        print(f"Clicked at {x}, {y}")

        if self.lol:
            sprite = random.choice(list(self.sprites.values()))
            sprite.display_at(x, y, sprite.duration, self.sound)

    def get_selected_macro_rows(self):
        selected_rows = []
        for row in range(self.ui_form.macrosTable.rowCount()):
            checkbox_item = self.ui_form.macrosTable.cellWidget(row, 0)
            if checkbox_item.checkbox.isChecked():
                selected_rows.append(row)

        return selected_rows


class CheckBoxCellWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.checkbox = QCheckBox()
        self.layout.addWidget(self.checkbox)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoHyakuretsu()
    window.show()
    sys.exit(app.exec_())
