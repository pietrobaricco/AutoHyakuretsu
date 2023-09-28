import pyautogui
from PyQt5.QtCore import QTimer

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class vlc(Macro):
    def run(self, screenshot_cv):
        if self.app.search_template("vlc_running", screenshot_cv):
            print("vlc seems to be running")
        else:
            if self.app.search_and_click("search", screenshot_cv):
                print("search area found")

                # dump some text in the search area with pyautogui, with 100 ms delay before starting
                QTimer.singleShot(200, lambda: pyautogui.typewrite("vlc", interval=0.1))
                NonBlockingDelay.wait(500)
                screenshot_cv = capture_screen()

                if self.app.search_and_click("vlc_app", screenshot_cv):
                    print("vlc seems to be installed")
