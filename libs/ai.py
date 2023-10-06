import json
import os

import openai
from texttable import Texttable


class bot:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def readableTable(self, cols, rows):
        table = Texttable(-1)
        # cols may be an array of dicts or just an array of strings
        table.header([c['text'] if isinstance(c, dict) else c for c in cols])

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
        prompt = "You will need to answer the following question based on a data table:\n\n" + question + "\n\n"
        prompt += "Before you answer, take a look at the following list of available fields, and return the names of the ones you will likely need:\n\n"
        prompt += "Fields:\n"
        for col in cols:
            prompt += col['text'] + "\n"
        prompt += "\n"
        prompt += " Return only JSON data, don't add any extra text as your answer must be in JSON format."
        prompt += " Specifically, return JSON array of strings where each string is one of the required fields:\n"

        json_fields = self.ask(prompt)
        fields = json.loads(json_fields)
        # if not valid json, return None
        if not isinstance(fields, list):
            return None

        print("To answer the question, you will need the following fields:", fields)

        reduced_rows = []
        for row in rows:
            reduced_row = {}
            for field in fields:
                if field in row:
                    reduced_row[field] = row[field]
            reduced_rows.append(reduced_row)

        final_prompt = "Given this data: \n\n" \
                       + self.readableTable(fields, reduced_rows) \
                       + "\n\n Answer the question:\n\n" \
                       + question \
                       + "\n\n" \
                       + "Return a JSON object containing the required variables:" \
                       + json.dumps(output_variables) \
                       + "\n\n" \
                       + "Don't add any extra text as your answer must be in JSON format.\n" \
                       + "Keep in mind that the data comes from OCR, it may not be perfect.\n"

        answer = self.ask(final_prompt)

        ret = json.loads(answer)
        if not isinstance(ret, dict):
            return None

        # check if all output variables are present
        for v in output_variables:
            if not v in ret:
                return None

        return ret

    def ask(self, question):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                  messages=[{"role": "user", "content": question}])

        return (completion.choices[0].message.content)
