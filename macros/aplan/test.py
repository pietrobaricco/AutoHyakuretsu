import pyautogui

from libs.capture import capture_screen
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class test(Macro):
    def run(self, screenshot_cv, parameters={}):

        aplan = aplan_utils(self)

        m = self.search_template("table-marker-1", screenshot_cv)

        rows, cols, funnel_pos = aplan.get_table_rows(screenshot_cv, m['x'], m['y'], m['x'] + 100, m['y'] + 200)

        print(self.app.bot.readableTable(cols, rows))

