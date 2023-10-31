import os
import time
from abc import abstractmethod, ABC

import pyautogui
from PyQt5.QtCore import QTimer

from libs.capture import get_matches, capture_screen
from libs.delay import NonBlockingDelay
from libs.png_templates import Template, load_templates


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

    def wait_for_template(self, name, timeout=60):
        total_time = 0
        while total_time < timeout:
            screenshot_cv = capture_screen(delay_ms=500)
            m = self.search_template(name, screenshot_cv)
            if m:
                return m, screenshot_cv
            total_time += 0.5
            print("Waiting for " + name + "...")
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
