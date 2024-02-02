import pyautogui
from PyQt5.QtCore import QTimer

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class run_program(Macro):

    def get_required_parameters(self):
        return ["search_string"]

    def run(self, screenshot_cv, parameters={}):

        m = self.search_and_click("search", screenshot_cv) \
            or self.search_and_click("search-96dpi", screenshot_cv)

        if m:
            print("search area found")

            # dump some text in the search area with pyautogui, with 100 ms delay before starting
            self.app.peon.write_text(parameters['search_string'], wait_ms=500)
            self.app.peon.enter()
        else:
            print("search area not found")

