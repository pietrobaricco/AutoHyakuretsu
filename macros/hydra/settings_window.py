from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class settings_window(Macro):

    def run(self, screenshot_cv):
        if not self.search_template("settings_win", screenshot_cv):
            if self.search_and_click("fedora_logo", screenshot_cv):
                NonBlockingDelay.wait(500)
                screenshot_cv = capture_screen()
                if self.search_and_click("sys_settings", screenshot_cv):
                    print("Gotcha!")
            else:
                print("Couldn't find the fedora logo")
        else:
            print("All good")
