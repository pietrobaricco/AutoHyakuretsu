import json

from libs.capture import capture_screen
from libs.macro import Macro


class process_email(Macro):

    def get_required_parameters(self):
        return ["prompt", "notes"]

    def run(self, screenshot_cv, parameters={}):

        email = parameters['prompt']
        if email:
            response = self.app.bot.ask('''
                You are part of a program which automates email handling. 
                Your task is to extract structured data from the email below and return it as JSON. 
                Make sure to strictly follow instructions and return only JSON data, don't add any extra text as your answer must be in JSON format.
                You must use the following format as ouput, xxx is used as placeholder:
                
                {
                    "date" : "xxx", # YYYY-MM-DD
                    "time" : "xxx", # HH:MM:SS
                    
                    "sender_email": "xxx",
                    "sender_company_name": "xxx", # e.g. "Onan Technogies S.r.l
                    "sender_company_name_main_keyword": "xxx", # used to search the entry later, eg. Onan
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
                                screenshot_cv = capture_screen(delay_ms=5000)
                                self.app.macros['aplan.offer_add_line'].run(screenshot_cv, {
                                    "product_code" : line_item['product_code'],
                                    "product_name" : line_item['product_name'],
                                    "quantity" : line_item['product_quantity']
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
