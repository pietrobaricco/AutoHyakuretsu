from libs.capture import capture_screen, ocr
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class settings_window(Macro):

    def run(self, screenshot_cv, parameters={}):
        if not self.search_template("settings_win", screenshot_cv):
            fedora_logo = self.search_template("fedora_logo", screenshot_cv)
            if fedora_logo:
                print("Found the fedora logo, clicking it")
                text, confidence = ocr(screenshot_cv, fedora_logo['x'] + 30, fedora_logo['y'] - 86, 1200, 26)
                print(text, confidence)
                self.app.click(fedora_logo['x'], fedora_logo['y'])
                NonBlockingDelay.wait(500)
                screenshot_cv = capture_screen()
                if self.search_and_click("sys_settings", screenshot_cv):
                    print("Gotcha!")
            else:
                print("Couldn't find the fedora logo")
        else:
            print("All good")
