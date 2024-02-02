import datetime
import json

import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class article_history(Macro):

    def get_required_parameters(self):
        return ["article_number", "quantity"]

    def run(self, screenshot_cv, parameters={}):
        aplan = aplan_utils(self)

        m, screenshot_cv = self.wait_for_template("article-search-page-marker")
        m = self.search_template("table-marker-minimal", screenshot_cv)

        today = datetime.datetime.now().strftime("%d/%m/%Y")

        if parameters['line_nr'] == 1:
            aplan.filter_table_by('[A,B]', screenshot_cv, "document-no-table-header", m['x'], m['y'], parse=False, clear_if_no_result=False)
            aplan.filter_table_by("<" + today, screenshot_cv, "date-table-header", m['x'], m['y'], parse=False, clear_if_no_result=False)

        rows, cols, funnel_pos = aplan.filter_table_by(parameters['article_number'], screenshot_cv, "part-number-table-header", m['x'], m['y'], clear_if_no_result=False)

        response = None

        if rows:
            print(self.app.bot.readableTable(cols, rows))

            question = '''
                                            We need to establish the correct markup percentage for a commercial offering of article ''' + parameters['article_number'] + '''
                                            Given a list of past offerings and orders of the same article, pick the most suitable one:
                                            
                                            - Pick a recent one
                                            - quantity less or equal than ''' + parameters['quantity'] + ''' units
                                    
                                            the column containing the word Margin is the one we are interested in: the value is provided as a float from 0 to 100.
                                            Return the number as a formatted string, decimal separator is a comma. Example: 67,3
                                            Provide a small recap of your reasoning in the reasoning field.
                                            '''

            response = self.app.bot.askTable(cols, rows, question,
                                             output_variables=["margin", "reasoning"])

        return response if response else {
            "margin": "n/a",
            "reasoning": "No suitable past offering found"
        }

