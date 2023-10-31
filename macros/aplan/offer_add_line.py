import json

import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class offer_add_line(Macro):

    def get_required_parameters(self):
        return ["product_code", "product_name", "quantity", "excluded_rows"]

    def run(self, screenshot_cv, parameters={}):

        excluded_rows = parameters['excluded_rows'] or [] if 'excluded_rows' in parameters else []
        parameters['excluded_rows'] = excluded_rows

        ok_marker = self.search_template("asterisk-green", screenshot_cv)
        if ok_marker:
            print("Search article Ready")
            # click on the search field
            self.app.click(ok_marker['x'] + 60, ok_marker['y'])
            self.app.peon.write_text(parameters['product_code'], interval=0.02, wait_ms=0)
            # click outside the search field
            self.app.click(ok_marker['x'] + 200, ok_marker['y'] + 100)

            screenshot_cv = capture_screen(delay_ms=2000)

            free_article = self.search_template("create-free-article", screenshot_cv)
            if free_article:
                print("Skip free article creation: article does not exist")
                self.app.peon.alt_n()
                return False

            select_article = self.search_template("select-article", screenshot_cv)
            if select_article:
                print("Multiple SKUs found")
                matching_address, funnel_pos, articles = self.extract_sku(screenshot_cv, parameters)
                if matching_address['row_number'] is not None:
                    row_nr_int = int(matching_address['row_number'])
                    self.app.click(funnel_pos['x'] + 100, funnel_pos['y'] + 10 + 16 * row_nr_int)
                    NonBlockingDelay.wait(30)
                    pyautogui.press('enter')

                    screenshot_cv = capture_screen(delay_ms=2000)
                    blocked = self.search_template("article-blocked", screenshot_cv)
                    if blocked:
                        print("Article blocked")
                        self.app.peon.ESC()
                        excluded_rows.append(matching_address)
                        if(len(articles) > len(excluded_rows)):
                            parameters['excluded_rows'] = excluded_rows
                            print("Retry with new parameters")
                            return self.run(screenshot_cv, parameters)
                        return False

            self.app.click(ok_marker['x'] + 60, ok_marker['y'])
            print("Article selected")

            for i in range(3):
                self.app.peon.right()

            self.app.peon.write_text(parameters['quantity'])
            self.app.peon.enter()

            self.app.peon.down()
            self.app.click(ok_marker['x'] + 200, ok_marker['y'] + 100)
        else:
            print("Search article not Ready")

    def extract_sku(self, screenshot_cv, parameters={}):
        aplan = aplan_utils(self)

        m = self.search_template("select-article-grid-anchor", screenshot_cv)

        if m:
            print("Found multiple skus")
            rows, cols, funnel_pos = aplan.get_table_rows(screenshot_cv, m['x'], m['y'], m['x'] + 100, m['y'] + 200)

            question = '''
                                Given a list of SKUs, return the row number which more likely matches the required article:

                                Code: ''' + parameters['product_code'] + '''
                                Name: ''' + parameters['product_name'] + '''
                                
                                Exclude rows: ''' + str(parameters['excluded_rows']) + '''
                                If you find a code that perfectly matches the input, us it regardless of the name.
                                '''

            response = self.app.bot.askTable(cols, rows, question,
                                             output_variables=["part_number", "description", "row_number"])

            if response:
                print("Found row for " + parameters['product_name'] + " at row " + str(response['row_number']))
                print(json.dumps(response, indent=4, sort_keys=True))
                return response, funnel_pos, rows

        else:
            print("No SKUs found")