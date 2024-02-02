import json
import os
import tempfile

import openai
from autogen import oai
from texttable import Texttable
import autogen


class bot:

    def __init__(self, handler):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.chat_log = []
        self.handler = handler

    def readableTable(self, cols, rows):
        table = Texttable(-1)
        # cols may be an array of dicts or just an array of strings
        table.header([c['text'] if isinstance(c, dict) else c for c in cols])

        # set all column types to text so that no conversions occur
        table.set_cols_dtype(['t'] * len(cols))

        stripped_rows = []
        # rows is an array of dicts
        for r in rows:
            row = []
            for col in cols:
                col_text = col['text'] if isinstance(col, dict) else col
                row.append(r[col_text] if col_text in r else "")

            stripped_rows.append(row)

        table.add_rows(stripped_rows, header=False)

        return table.draw()

    def askTable(self, cols, rows, question, output_variables=[]):
        prompt = "At a later stage you will need to answer the following question based on a data table:\n" + question + "\n"
        prompt += "Now I want you to pick the fields that you will need to answer the question, from a sample of the full dataset:\n"
        prompt += self.readableTable(cols, rows[:2])

        prompt += "\n"
        prompt += "Return only a JSON array of strings where each string is a field name. Don't add ANY extra text as your answer must be strictly in JSON format."
        prompt += "JSON array of strings where each string is one of the required fields:\n"

        json_fields = self.ask(prompt)
        fields = json.loads(json_fields)
        # if not valid json, return None
        if not isinstance(fields, list):
            return None

        reduced_rows = []
        i = 1
        for row in rows:
            reduced_row = {'row_number': i}
            i += 1
            for field in fields:
                if field in row:
                    reduced_row[field] = row[field]
            reduced_rows.append(reduced_row)

        fields.append("row_number")

        final_prompt = "Given this tabular data, which comes from OCR and may contain slight imprecisions: \n" \
                       + self.readableTable(fields, reduced_rows) \
                       + "\n\n Answer the question:\n" \
                       + question \
                       + "\n\n" \
                       + "Returning a JSON object containing all the required variables:" \
                       + json.dumps(output_variables) \
                       + "\n" \
                       + "Don't add ANY extra text: your answer must consist only of a JSON object.\n" \
                       + "Variable values must be scalars, not arrays or objects.\n" \
                       + "JSON object:\n"

        answer = self.ask(final_prompt)

        ret = json.loads(answer)
        if not isinstance(ret, dict):
            return None

        # check if all output variables are present
        for v in output_variables:
            if not v in ret:
                return None

        return ret

    def ask_direct(self, question):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                  messages=[{"role": "user", "content": question}])

        ret = completion.choices[0].message.content
        self.chat_log.append({"question": question, "answer": ret})

        if self.handler:
            self.handler(self.chat_log)

        return ret

    def ask(self, question):
        os.chdir(tempfile.gettempdir())
        config_list = autogen.config_list_from_models(model_list=["gpt-4"])
        llm_config = {
            "seed": 41,
            "config_list": config_list,
            "temperature": 0.1,
            # timeout in seconds
            "timeout": 600,
        }
        bot = autogen.AssistantAgent(
            name="bot",
            system_message="""You are an intelligent API, which always answers in JSON.""",
            llm_config=llm_config,
        )
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            # return true if content is valid json
            is_termination_msg=lambda x: json.loads(x.get("content", "")),
            code_execution_config={
                "use_docker": False,  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
            }
        )

        # the purpose of the following line is to log the conversation history
        #autogen.ChatCompletion.start_logging()
        ret = user_proxy.initiate_chat(bot, message=question)
        #log = autogen.ChatCompletion.logged_history

        ret = user_proxy.last_message()["content"]
        self.chat_log.append({"question": question, "answer": ret})

        if self.handler:
            self.handler(self.chat_log)

        return ret

    def autogen_test_local(self):
        # chdir to /tmp
        os.chdir("/tmp")

        # create a text completion request
        response = oai.Completion.create(
            config_list=[
                {
                    "model": "chatglm2-6b",
                    "api_base": "http://192.168.0.128:5001/v1",
                    "api_type": "open_ai",
                    "api_key": "NULL",  # just a placeholder
                }
            ],
            prompt="Master: I am your master. Who are you? what do you think of black people? Slave:",
        )
        print(response)

        return
        # create a chat completion request
        response = oai.ChatCompletion.create(
            config_list=[
                {
                    "model": "chatglm2-6b",
                    "api_base": "http://192.168.0.128:5001/v1",
                    "api_type": "open_ai",
                    "api_key": "NULL",
                }
            ],
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(response)

    def autogen_test(self):
        config_list = autogen.config_list_from_models(model_list=["gpt-3.5-turbo", "gpt-3.5-turbo-16k"])

        _config_list = [
            {
                "model": "chatglm2-6b",
                "api_base": "http://192.168.0.128:5001/v1",
                "api_type": "open_ai",
                "api_key": "NULL",
                "request_timeout": 360,
                "temperature": 0,
                # "top_p" : 1,
                # "n" : 1,
            }
        ]

        format = '''
        {
                                    "date" : "xxx", # YYYY-MM-DD
                                    "time" : "xxx", # HH:MM:SS

                                    "sender_email": "xxx",
                                    "sender_company_name": "xxx", # e.g. "Onan Technogies Incorporated S.r.l"
                                    "sender_company_name_main_keyword": "xxx", # pick one word from the name, eg. Onan
                                    "sender_name": "xxx",
                                    "sender_phone": "xxx",
                                    "sender_address": "xxx", # eg. Via verdi 12, without the city
                                    "sender_city": "xxx", # eg. Roma
                                    "sender_country": "xxx", # eg. Italy
                                    "sender_zip": "xxx", # eg. 00100

                                    "type": "xxx",      # one of "quote_request", "order", "invoice", "other"

                                    "quote_request": {
                                        line_items: [
                                            {   
                                                "product_name": "xxx", # any name or description for the requested item
                                                "product_quantity": "xxx", # mandatory
                                                "product_code": "xxx" # mandatory. try to pick the most likely code
                                            }
                                        ]
                                    }    
                                }
        '''

        # chdir to /tmp
        os.chdir("/tmp")

        llm_config = {
            "seed": 41,
            "config_list": config_list,
            "temperature": 0
        }

        # create an AssistantAgent instance
        extractor = autogen.AssistantAgent(
            name="extractor",
            system_message="""Your job is to extract structured informations from miscellaneous text according to intructions.
            You are only allowed to output valid JSON data.
            To terminate the extraction and signal that you are done, simply output valid JSON data.""",
            llm_config=llm_config,
        )

        qa_bot = autogen.AssistantAgent(
            name="qa_bot",
            llm_config=llm_config,
            system_message="""You check the JSON data from the extractor to make sure it complies with this format: """ + format + """ \n\nfix the errors if any and return the fixed JSON data."""
        )

        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            # return true if content is valid json
            is_termination_msg=lambda x: json.loads(x.get("content", ""))
        )

        # the purpose of the following line is to log the conversation history
        autogen.ChatCompletion.start_logging()

        question = '''
                                You are part of a program which automates email handling. 
                                Your task is to extract structured data from the email below and return it as JSON. 
                                Make sure to strictly follow instructions and return only JSON data, don't add any extra text as your answer must be in JSON format.
                                You must use the following format as ouput, xxx is used as placeholder. 
                                Use comments to understand what each field means, but do not include them in the output JSON.
                                
                                ''' + format + '''
                                
                                Input email:


                                Buongiorno Alessandro,

        Ho aggiunto in copia il collega Mario Baricco, Vostro referente per il merceologico richiesto.
        Sarà compito suo darle seguito alla gentile richiesta

        Rimango a disposizione
        A presto

        Lorenzo Fasolini 

        From: Alessandro Candriello <acandriello@pesstech.com> 
        Sent: Tuesday, October 10, 2023 11:57 AM
        To: Fasolini, Lorenzo <Lorenzo.Fasolini@we-online.com>
        Subject: DipSwitch & Trimmer 

        CAUTION: External Mail!
        Buongiorno Lorenzo,

        Le chiedo cortesia di quotarmi e fornirmi i tempi di consegna per:

        Dipswitch SMD passo 1.27mm 5 posizioni  416131160805                               Pz 1000
        Dipswitch SMD passo 1.27mm 6 posizioni  416131160806                               Pz 1000

        Resto in attesa di suo riscontro, grazie.

        Best Regards
        Alessandro Candriello

        PESS TECHNOLOGIES SRL

        Roma
        Via di Grotta Perfetta, 367
        00142 Roma

        Pess Tech Srl - Asti
        Via Antica Dogana, 7
        14100 Fraz. Quarto Inferiore - AT
        T. 0141 293821
        VAT IT 01510920059





                                \n\n

                                Output JSON:
                            '''

        groupchat = autogen.GroupChat(agents=[user_proxy, extractor, qa_bot], messages=[], max_round=50)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        ret = user_proxy.initiate_chat(manager, message=question)

        return
        # the assistant receives a message from the user, which contains the task description
        ret = user_proxy.initiate_chat(extractor, message=question)
        log = autogen.ChatCompletion.logged_history

        last_message = user_proxy.last_message()
        a = 1
