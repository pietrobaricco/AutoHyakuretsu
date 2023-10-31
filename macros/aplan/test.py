import pyautogui

from libs.capture import capture_screen
from libs.macro import Macro


class test(Macro):
    def run(self, screenshot_cv, parameters={}):

        m = self.search_template("address-search-multi", screenshot_cv) \
            or self.search_template("address-search-multi-2", screenshot_cv) \
            or self.search_template("address-search-multi-3", screenshot_cv)

        # matches = r = self.search_templates(screenshot_cv, ["address-search-multi", "address-search-multi-2", "address-search-multi-3"])
        print(m)

