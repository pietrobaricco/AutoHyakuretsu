import pyautogui

from libs.capture import capture_screen
from libs.macro import Macro


class clear(Macro):
    def run(self, screenshot_cv, parameters={}):
        title = self.search_template("title", screenshot_cv)
        if title:
            print("App is running")

            # close annoying requesters
            r = self.search_template("load-last-config", screenshot_cv)
            if r:
                print("Found the load last config requester")
                # focus the requester
                self.app.click(r['center_x'], r['center_y'])
                # send ESC
                pyautogui.press('esc')
                screenshot_cv = capture_screen(delay_ms=2000)

            # close all close buttons
            while True:
                m = self.search_and_click("x-close", screenshot_cv)
                if not m:
                    break
                screenshot_cv = capture_screen(delay_ms=2000)

        else:
            print("App is not running")
            return
