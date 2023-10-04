import os
import time
from abc import abstractmethod, ABC

import pyautogui
from PyQt5.QtCore import QTimer

from libs.capture import get_matches
from libs.delay import NonBlockingDelay
from libs.png_templates import Template, load_templates


class Macro(ABC):
    templates: list[Template] = []

    def __init__(self, app, name, templates_dir):
        # AutoHyakuretsu

        self.app = app
        self.name = name
        self.templates_dir = templates_dir
        self.templates = load_templates(self.templates_dir)
        self.parameters = {}

    @abstractmethod
    def run(self, screenshot_cv, parameters={}):
        pass

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

    def search_and_click(self, name, screenshot_cv, x_offset=0, y_offset=0, nr_clicks=1):
        m = self.search_template(name, screenshot_cv)
        if m:
            self.app.click(m['x'] + x_offset, m['y'] + y_offset, nr_clicks)
            print(name + "found at date " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            return m
        return False

    def search_template(self, name, screenshot_cv):
        matches1 = self.search_templates(screenshot_cv, [name])
        m = self.get_first_match(matches1, name)
        return m

    def write_text(text, interval=0.1, wait_ms=0):
        QTimer.singleShot(200, lambda: pyautogui.typewrite(text, interval=interval))
        NonBlockingDelay.wait(wait_ms)

def search_macros(directory):
    macros = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
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
