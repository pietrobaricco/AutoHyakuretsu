import json

import cv2
import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class new_offer(Macro):

    def get_required_parameters(self):
        return ["originator"]

    def run(self, screenshot_cv, parameters={}):

        originatorObj = json.loads(parameters['originator'])

        ok_marker, screenshot_cv = self.wait_for_template("address-page-ok")
        if ok_marker:
            print("New offer - Address page ok")
            # shift + alt + f5 per aprire la pagina di nuova offerta
            self.app.peon.shift_alt_f5()
            m, screenshot_cv = self.wait_for_template("offer-page-marker")

            # chiude popup se presente
            self.app.macros['aplan.popup_ok'].run(screenshot_cv, {})

            select_contact = offer_ready = None
            while not (select_contact or offer_ready):
                select_contact, screenshot_cv = self.wait_for_template("select-contact-person", 1)
                offer_ready, screenshot_cv = self.wait_for_template("offer-ready", 1)

            # esce un popup di anagrafiche, deve selezionare quello più probabile come mittente della mail nome e cognome:
            if select_contact:
                print("Selezionare un contatto")
                matching_address, funnel_pos = self.extract_address(screenshot_cv, originatorObj)
                if matching_address['row_number'] is not None:
                    print("NEW OFFER: Found matching address at row " + str(matching_address['row_number']))
                    self.app.click(funnel_pos['x'] + 100, funnel_pos['y'] + 10 + 16 * matching_address['row_number'])
                    NonBlockingDelay.wait(30)
                    pyautogui.press('enter')
                    screenshot_cv = capture_screen(delay_ms=5000)

                    if self.search_template("select-delivery-address", screenshot_cv):
                        print("Skip delivery address selection")
                        self.app.peon.ESC()
                        screenshot_cv = capture_screen(delay_ms=5000)

                    if self.search_template("select-invoice-address", screenshot_cv):
                        print("Skip invoice address selection")
                        self.app.peon.ESC()
                        screenshot_cv = capture_screen(delay_ms=5000)

            offer_ready, screenshot_cv = self.wait_for_template("offer-ready")
            if offer_ready:
                print("Offer ready")
                return True
        else:
            cv2.imshow("screenshot", screenshot_cv)
            print("New offer - Address page not ok")
    def extract_address(self, screenshot_cv, originatorObj):
        aplan = aplan_utils(self)

        m = self.search_template("address-search-multi-popup-1", screenshot_cv)

        if m:
            print("Found contact list popup")

            rows, cols, funnel_pos = None, None, None
            # 1 search by last name
            if originatorObj['last_name']:
                rows, cols, funnel_pos = self.filter_table_by(originatorObj['last_name'], screenshot_cv, "search-last-name-table-header", m['x'], m['y'], 20)
            if not rows and originatorObj['name']:
                rows, cols, funnel_pos = self.filter_table_by(originatorObj['name'], screenshot_cv, "search-first-name-table-header", m['x'], m['y'])
            if not rows:
                rows, cols, funnel_pos = aplan.get_table_rows(screenshot_cv, m['x'], m['y'], m['x'] + 100, m['y'] + 200)

            question = '''
                                Given a list of contact persons for a commercial offer, return the row number of the contact person that matches the following criteria: 
                                
                                - is the originator of the request that generated the offer (via email or other means)
                                - or is someone from the purchasing department of the company that originated the request
                                - or the best match based on your judgement  

                                Originator: ''' + json.dumps(originatorObj) + '''
                                Matching row nr:
                                '''

            response = self.app.bot.askTable(cols, rows, question, output_variables=["row_number", "contact_name"])

            if response:
                print("Found row for " + json.dumps(originatorObj) + " at row " + str(response['row_number']))
                print(json.dumps(response, indent=4, sort_keys=True))
                return response, funnel_pos

        else:
            print("No contact list popup found")


    def filter_table_by(self, value, screen_img, header_template, table_x, table_y, x_offset = 0):

        aplan = aplan_utils(self)

        row_width = screen_img.shape[1]

        cropped = screen_img[table_y:table_y+100, table_x:table_x+row_width]

        search_box = self.search_template(header_template, cropped)
        if search_box:
            print("Filtering the list by name")
            self.app.click(table_x + search_box['center_x'] + x_offset, table_y + search_box['center_y'] + 20)
            self.app.peon.write_text(value, interval=0.02, wait_ms=0)
            self.app.peon.enter()

            screenshot_cv = capture_screen(delay_ms=3000)

            rows, cols, funnel_pos = aplan.get_table_rows(screenshot_cv, table_x, table_y, table_x + 100, table_y + 200)

            if not rows:
                print("No results found, rolling search back")
                self.app.click(table_x + search_box['center_x'], table_y + search_box['center_y'] + 20)
                self.app.peon.END()
                for i in range(len(value) + 2):
                    self.app.peon.backspace()

            return rows, cols, funnel_pos
        else:
            print("No search box found")
            return None, None, None