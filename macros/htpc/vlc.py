import pyautogui
from PyQt5.QtCore import QTimer

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class vlc(Macro):

    def get_required_parameters(self):
        return ["search_string"]

    def run(self, screenshot_cv, parameters={}):
        if self.search_template("vlc_running", screenshot_cv):
            print("vlc seems to be running")
        else:
            if self.search_and_click("search", screenshot_cv):
                print("search area found")

                # dump some text in the search area with pyautogui, with 100 ms delay before starting
                self.app.peon.write_text(parameters['search_string'], wait_ms=500)
                screenshot_cv = capture_screen()

                if self.search_and_click("vlc_app", screenshot_cv):
                    print("vlc seems to be installed")
