from libs.capture import capture_screen
from libs.macro import Macro


class popup_ok(Macro):
    def run(self, screenshot_cv, parameters={}):

        # close all popups
        while True:
            m = self.search_and_click("popup-1-ok", screenshot_cv) \
                or self.search_and_click("popup-2-ok", screenshot_cv)

            if not m:
                print("No more popups")
                break
            print("Found popup, closing")
            screenshot_cv = capture_screen(delay_ms=2000)


