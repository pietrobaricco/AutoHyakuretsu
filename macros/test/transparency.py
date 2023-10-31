import pyautogui

from libs.capture import capture_screen
from libs.macro import Macro


class transparency(Macro):
    def run(self, screenshot_cv, parameters={}):

        matches = r = self.search_templates(screenshot_cv, ["z_transparent"])
        print(matches)

