import os
import time
from abc import abstractmethod, ABC

import pyautogui

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QDialog

from libs.capture import get_matches, capture_screen
from libs.delay import NonBlockingDelay
from libs.png_templates import Template, load_templates
from ui.askPause import Ui_AskPauseWindow


class Macro(ABC):
    templates: list[Template] = []

    def __init__(self, app, name, templates_dir):
        self.app = app
        self.name = name
        self.templates_dir = templates_dir
        self.templates = load_templates(self.templates_dir)
        self.parameters = {}

    @abstractmethod
    def run(self, screenshot_cv, parameters={}):
        pass

    def pause(self, message):
        dialog_window = Ui_AskPauseWindow()

        dialog = QDialog()
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        dialog_window.setupUi(dialog)

        dialog_window.message_browser.setText(message)
        dialog_window.resume_button.clicked.connect(dialog.accept)
        dialog_window.terminate_button.clicked.connect(dialog.reject)

        result = dialog.exec_()

        return result == QDialog.Accepted

    def get_required_parameters(self):
        return []

    def get_first_match(self, matches, name):
        m = matches.get(name, [])
        if len(m) > 0:
            return m[0]
        return None

    def search_templates(self, cv_image, names):
        filtered_arr = [p for p in self.templates if p.name in names]
        matches = get_matches(filtered_arr, cv_image)
        return matches

    def search_and_click(self, name, screenshot_cv, x_offset=0, y_offset=0, nr_clicks=1, center=True):
        m = self.search_template(name, screenshot_cv)
        if m:
            cx = m['center_x'] if center else m['x']
            cy = m['center_y'] if center else m['y']
            self.app.click(cx + x_offset, cy + y_offset, nr_clicks)
            print(name + "found at date " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            return m
        return False

    def search_template(self, name, screenshot_cv):
        matches1 = self.search_templates(screenshot_cv, [name])
        m = self.get_first_match(matches1, name)
        return m

    def wait_for_template(self, name, timeout=15, pause_on_timeout=True):
        total_time = 0
        while total_time < timeout:
            screenshot_cv = capture_screen(delay_ms=500)
            m = self.search_template(name, screenshot_cv)
            if m:
                return m, screenshot_cv
            total_time += 0.5
            print("Waiting for " + name + "...")

        if pause_on_timeout:
            if self.pause("Template " + name + " not found. Continue?"):
                return self.wait_for_template(name, timeout)
            else:
                raise TerminatedError("Template " + name + " not found")

        return None, screenshot_cv

def search_macros(directory):
    macros = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath) and not filename == "libs":
            print(f"Loading and executing modules in {filename} directory:")
            # recursively load macros in subdirectories
            macros += search_macros(filepath)
            print("Done.")
        else:
            if filename.endswith(".py") and filename != "__init__.py":
                macro_name = filename[:-3]
                module_name = directory
                macros.append({"name": macro_name, "module": module_name})
    return macros


class TerminatedError(Exception):
    def __init__(self, message="Macro terminated by user"):
        self.message = message
        super().__init__(self.message)
