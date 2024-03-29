import json

import keyboard
import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class person_search(Macro):

    def get_required_parameters(self):
        return ["first_name", "last_name", "company_name", "email"]

    def extract_person(self, screenshot_cv, parameters={}):
        aplan = aplan_utils(self)

        m = self.search_template("result-multi-1", screenshot_cv)

        if m:
            print("Found multiple addresses")
            rows, cols, funnel_pos = aplan.get_table_rows(screenshot_cv, m['x'], m['y'], m['x'] + 100, m['y'] + 200)

            question = '''
                                Given a list of customers, return the row number which more likely matches a contact we 
                                have the following information about:

                                First name: ''' + parameters['first_name'] + '''
                                Last name: ''' + parameters['last_name'] + '''
                                Company name: ''' + parameters['company_name'] + '''
                                Email: ''' + parameters['email'] + '''
                                '''

            response = self.app.bot.askTable(cols, rows, question,
                                             output_variables=["row_number", "customer_name", "position"])

            if response:
                print("Found row for " + parameters['last_name'] + " at row " + str(response['row_number']))
                print(json.dumps(response, indent=4, sort_keys=True))
                return response, funnel_pos

        else:
            print("One or zero persons found")

    def run(self, screenshot_cv, parameters={}):

        # reset the desktop
        self.app.macros['aplan.clear'].run(screenshot_cv, {})

        # focus the window click on the title
        t = self.search_and_click("title", screenshot_cv)
        if t:
            # send hotkey to open the search window
            self.app.peon.ctrl_f2()

            # search box for name
            name_box, screenshot_cv = self.wait_for_template("person_search_name_header")
            if name_box:
                print("Found the name search box")
                self.app.click(name_box['center_x'], name_box['center_y'] + 20)
                self.app.peon.write_text('%' + parameters['last_name'] + '%', interval=0.02, wait_ms=0)
                self.app.peon.enter()

                result_ok = result_multi_ok = None
                retries = 0
                while not (result_ok or result_multi_ok):
                    retries += 1
                    if(retries > 10):
                        if self.pause("Person not found. Select one manually and press resume when done"):
                            break
                        else:
                            return False

                    result_ok, screenshot_cv = self.wait_for_template("address-page-ok", 1, False)
                    result_multi_ok, screenshot_cv = self.wait_for_template("result-multi-1", 1, False)

                if result_multi_ok:
                    print("Found multiple persons")
                    screenshot_cv = capture_screen(delay_ms=100)
                    ret = self.extract_person(screenshot_cv, parameters)
                    if ret:
                        matching_address, funnel_pos = ret

                        if matching_address['row_number'] is not None:

                            print("Found matching person at row " + str(matching_address['row_number']))
                            self.app.click(funnel_pos['x'] + 100, funnel_pos['y'] + 10 + 16 * matching_address['row_number'])
                            NonBlockingDelay.wait(30)
                            self.app.peon.enter()

                result_ok, screenshot_cv = self.wait_for_template("address-page-ok")

                if result_ok:
                    print("We are on the address page")
                    # chiude popup se presente
                    self.app.macros['aplan.popup_ok'].run(screenshot_cv, {})
                    return True
                else:
                    print("WTF")
                    return False

        else:
            print("App is not running")
            return
