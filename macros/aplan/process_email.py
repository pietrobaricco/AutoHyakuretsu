import json

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
                    "sender_company_name": "xxx",
                    "sender_name": "xxx",
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
                    # pretty print
                    print(json.dumps(data, indent=4, sort_keys=True))
                else:
                    print("Invalid JSON")
            else:
                print("No response")
        else:
            print("No email found")
