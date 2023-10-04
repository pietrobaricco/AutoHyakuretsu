import time

import cv2

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro

class multiple_searches(Macro):

    def run(self, screenshot_cv, parameters={}):

        # call a sub macro, example
        search1 = "how old is the universe"
        search2 = "how old is the earth"

        self.app.macros['chatgpt.ask_something'].run(screenshot_cv, {"prompt": search1})
        self.app.macros['chatgpt.ask_something'].run(screenshot_cv, {"prompt": search2})



