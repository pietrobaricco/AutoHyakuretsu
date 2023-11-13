import datetime
import json

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro
from macros.aplan.libs.aplan import aplan_utils


class process_email(Macro):

    def get_required_parameters(self):
        return ["prompt", "notes"]

    def run(self, screenshot_cv, parameters={}):

        valid_prefixes = [
            558, 609, 610, 613, 620, 621, 622, 623, 612, 625, 627, 620, 624, 639, 645, 646,
            688, 648, 679, 649, 653, 662, 665, 686, 687, 690, 614, 629, 651, 615, 632,
            634, 619, 638, 691, 696, 695, 746, 970, 971, 977, 963, 970, 971
        ]

        aplan = aplan_utils(self)

        email = parameters['prompt']
        if email:
            response = self.app.bot.ask('''
                You are part of a program which automates email handling. 
                Your task is to extract structured data from the email below and return it as JSON. 
                Make sure to strictly follow instructions and return only JSON data, don't add any extra text as your answer must be in JSON format.
                
                Details about how to extract the names:                
                
                * sender_company_name:
                    If the email has a signature section, use the name as provided in the signature. Otherwise, infer it from the sender email address.
                
                * sender_company_name_main_keyword:
                    It will be used to search the record of the company in the ERP.
                    Therefore, pick exactly -one- word from the sender company name field, the most significant one.
                    Strip non alphanumeric characters, consider spaces, and don't use common and non differentiating strings such as the company type (spa, srl. ltd, inc, etc)
                    
                    some examples (name -> main_keyword):
                    1) "C.M.P. Onan Technogies S.r.l" -> "onan"
                    2) "Oriundo tech snc" -> "oriundo"
                    3) "Blue Whale Spa, www.bluewhale.com" -> "whale"
                
                You must use the following format as ouput, xxx is used as placeholder:
                {
                    "date" : "xxx", # YYYY-MM-DD
                    "time" : "xxx", # HH:MM:SS
                    
                    "sender_email": "xxx",
                    "sender_company_name": "xxx", # e.g. "C.M.P. Onan Technogies S.r.l
                    "sender_company_name_main_keyword": "xxx", # onan
                    "sender_name": "xxx", # e.g. "John"
                    "sender_last_name": "xxx", # e.g. "Doe"
                    "sender_phone": "xxx",
                    "sender_address": "xxx",
                    "sender_city": "xxx",
                    "sender_country": "xxx",
                    "sender_zip": "xxx",
                    
                    "type": "xxx",      # one of "quote_request", "order", "invoice", "other"
                    
                    "quote_request": {
                        line_items: [
                            {   
                                "product_name": "xxx",
                                "product_quantity": "xxx",
                                
                                # search for product codes in this format: ^[0-9]{12,15}(|[A-Z]{2})$
                                # sometimes codes are provided by customers with spaces, dashes or other characters which you must ignore
                                "product_code": "xxx" 
                            }
                        ]
                    }    
                }
                
                Notes:\n\n''' + parameters['notes'] + '''\n\n
                Input email:\n\n''' + email + '''\n\n
                
                Output JSON:
            ''')

            if response:
                data = json.loads(response)
                if data:
                    address = self.app.macros['aplan.address_search'].run(screenshot_cv, {
                        "name": data['sender_company_name_main_keyword'],
                        "address": data['sender_address'],
                        "town": data['sender_city'],
                        "phone_no": data['sender_phone']
                    })
                    if address:
                        m, screenshot_cv = self.wait_for_template("article-history-button")
                        self.search_and_click("article-history-button", screenshot_cv)

                        m, screenshot_cv = self.wait_for_template("article-search-page-marker")

                        for line_item in data['quote_request']['line_items']:
                            if line_item['product_code'] and int(line_item['product_code'][0:3]) in valid_prefixes:

                                margin = self.app.macros['aplan.article_history'].run(screenshot_cv, {
                                    "article_number": line_item['product_code'],
                                    "quantity": line_item['product_quantity']
                                })

                                print ("Margin for " + line_item['product_code'] + " is " + str(margin['margin']))
                                line_item['margin'] = margin['margin']
                                line_item['reasoning'] = margin['reasoning']

                        # back to the address page
                        self.app.peon.ESC()

                        originator = {
                            "name": data['sender_name'],
                            "last_name": data['sender_last_name'],
                            "email": data['sender_email'],
                            "phone": data['sender_phone'],
                            "address": data['sender_address'],
                            "city": data['sender_city'],
                            "country": data['sender_country'],
                            "zip": data['sender_zip']
                        }
                        offer = self.app.macros['aplan.new_offer'].run(screenshot_cv, {
                            "originator": json.dumps(originator),
                        })
                        if offer:
                            print("New offer created")
                            for line_item in data['quote_request']['line_items']:

                                if line_item['product_code'] and int(line_item['product_code'][0:3]) in valid_prefixes:
                                    self.app.macros['aplan.offer_add_line'].run(screenshot_cv, {
                                        "product_code" : line_item['product_code'],
                                        "product_name" : line_item['product_name'],
                                        "quantity" : line_item['product_quantity'],
                                        "margin_percent" : line_item['margin']
                                    })
                                else:
                                    print("Invalid product code: " + line_item['product_code'])

                            # crea le posizioni
                            self.app.peon.alt_q()

                            screenshot_cv = capture_screen(delay_ms=2000)

                            #self.search_and_click("offer-stock-trend-button", screenshot_cv)
                            #NonBlockingDelay.wait(5000)

                            #self.search_and_click("offer-cp-update-button", screenshot_cv)
                            #NonBlockingDelay.wait(10000)

                            today_it = datetime.datetime.now().strftime("%d/%m/%Y")
                            self.app.macros['aplan.offer_fill_fields'].run(screenshot_cv, {
                                "fu_status": "MaBar",
                                "contact2": "C",
                                "your_inquiry": "Mail del " + today_it
                            })

                            return True
                        else:
                            print("New offer not created!")
                else:
                    print("Invalid JSON")
            else:
                print("No response")
        else:
            print("No email found")
