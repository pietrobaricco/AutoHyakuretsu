import json

import pyautogui

from libs.capture import capture_screen
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class address_search(Macro):

    def _get_required_parameters(self):
        return ["name","address","town","phone_no"]

    def run(self, screenshot_cv, parameters={}):

        aplan = aplan_utils(self)

        # reset the desktop
        self.app.macros['aplan.clear'].run(screenshot_cv, {})

        # focus the window click on the title
        t = self.search_and_click("title", screenshot_cv)
        if t:
            # send alt + f2 to open the search window
            pyautogui.hotkey('alt', 'f2')
            screenshot_cv = capture_screen(delay_ms=2000)

            # search box for name
            name_box = self.search_template("search_name", screenshot_cv)
            if name_box:
                print("Found the name search box")
                self.app.click(name_box['center_x'], name_box['center_y'] + 20)
                self.write_text(parameters['name'] + "\n", interval=0.02, wait_ms=0)
                screenshot_cv = capture_screen(delay_ms=2000)

                m = self.search_template("address-search-multi", screenshot_cv)
                if m:
                    print("Found multiple addresses")
                    rows, cols = aplan.get_table_rows(screenshot_cv, m['x'], m['y'], m['x'] + 100, m['y'] + 200)

                    question = '''
                        Given a list of customers, return the row number which more likely matches a contact we 
                        have the following information about:
                         
                        Name: ''' + parameters['name'] + '''
                        Address: ''' + parameters['address'] + '''
                        Town: ''' + parameters['town'] + '''
                        Phone no: ''' + parameters['phone_no']

                    response = self.app.bot.askTable(cols, rows, question, output_variables=["row_number", "customer_code", "customer_name"])

                    if response:
                        print("Found row for " + parameters['name'] + " at row " + str(response['row_number']))
                        print(json.dumps(response, indent=4, sort_keys=True))

                else:
                    print("One or zero addresses found")

        else:
            print("App is not running")
            return



