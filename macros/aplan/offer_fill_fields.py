import json

import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class offer_fill_fields(Macro):

    def get_required_parameters(self):
        return ["fu_status", "contact2", "your_inquiry"]

    def run(self, screenshot_cv, parameters={}):

        # focus the window click on the title
        t = self.search_and_click("title", screenshot_cv)

        print("Constants")
        self.app.peon.alt_8()

        marker_pos, screenshot_cv = self.wait_for_template("offer-flags-sales-price-marker")
        if marker_pos:
            # custom tariffs, default is ON
            self.app.click(marker_pos['x'] + 16, marker_pos['y'] + 50)
            NonBlockingDelay.wait(100)

            self.app.click(marker_pos['x'] + 16, marker_pos['y'] + 112)
            NonBlockingDelay.wait(100)

            self.app.click(marker_pos['x'] + 16, marker_pos['y'] + 136)
            NonBlockingDelay.wait(100)

        print("Fill fields")

        field_pos = self.search_template("offer-field-title", screenshot_cv)
        if field_pos:
            self.app.click(field_pos['x'] + 150, field_pos['y'] + 10)
            self.app.peon.write_text(parameters['fu_status'], interval=0.02, wait_ms=1000)

        print("-")

        field_pos = self.search_template("offer-field-contact2", screenshot_cv)
        if field_pos:
            self.app.click(field_pos['x'] + 150, field_pos['y'] + 10)
            self.app.peon.write_text(parameters['contact2'], interval=0.02, wait_ms=1000)

        print("-")

        field_pos = self.search_template("offer-field-your-inquiry", screenshot_cv)
        if field_pos:
            self.app.click(field_pos['x'] + 150, field_pos['y'] + 10)
            self.app.peon.write_text(parameters['your_inquiry'], interval=0.02, wait_ms=1000)

        return True