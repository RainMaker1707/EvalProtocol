from bert_score import score
import re
import pandas as pd
import json
import warnings
from openai import OpenAI, OpenAIError

with open("BERT/configs/config.json", "r") as file:
    config = json.loads(file.read())
    file.close()

print(config)

client = OpenAI(api_key=config.get("api_key"))

prompt = """
            I want you to act as a cyber security analyst. You work in a Computer Emergency Response Team (CERT).
            I will provide you with a file containing network data. Your job is to detect if the current file contains significant proofs of infection.
            If it is infected you will answer by filling this template:
            ```md
            # Device infected
            ## Matching URLs
                <%list_of_matching_urls_if_any%>

            ## Explanations
                - <%command_spotted%>
            ```
            If it is safe you will fill this markdown template:
            ```md
            # Device safe
            ## Matching URLs
                <%list_of_matching_urls_if_any%>

            ## Explanations
                <%explanation%>
            ```
            The part between "<%...%>" need to be filled with the appropriate content.
            To achieve your task your have access to a documentation file about the suspected Command and Control framework that would be used.
            This documentation contains all what you need to understood and analyze the data file provided.
            Read this documentation at least third time before analyzing the data or trying anything.
            All URLs matching a possibility of Slimper used URL should be in the replacement of <%list_of_matching_urls_if_any%>.
            To match these URL you can use the following RegEx: \/[a-zA-Z0-9._\-\/]+
            <%command_spotted%> should be replaced by a list of the command found in the data segment sent by the SLimper C2 server in an HTTP response.
         """

question = "Analyze the file 'ls_kill.json' to detect infection of Slimper C2 framework."


class Template():
    def __init__(self, filename):
        self.filename = filename
        self.load()
        self.filled = None

    def load(self):
        with open(self.filename) as file:
            self.content = file.readlines()
            file.close()

    def fill(self, filename, no_save=False):
        if self.filled != None and no_save == False:
            print("Set the no_save argument to True to erase old filled template")
            return
        self.filled = ""
        if(filename[-4:] == ".csv"):
            df = pd.read_csv(filename)
            csv = df['request_uri'].dropna() 
            urls = csv.apply(lambda x: re.findall(r'\/[a-zA-Z0-9._\-\/]+', x))
            urls = [e[0] for e in urls.to_list()]
            commands = [e for e in df['data'].dropna().to_list()]
            for line in self.content:
                if "<%list_of_matching_urls_if_any%>" in line:
                    for url in urls:
                        self.filled += f'\t- {url}\n'
                elif "<%command_spotted%>" in line:
                    if not "ls" in commands or not "kill" in commands:
                        self.filled += "\t- No command detected\n"
                    else: 
                        self.filled += "\t- Command(s) spotted\n"
                        for command in commands:
                            if command == "ls" or command == "kill":
                                self.filled += f'\t\t- {command}\n'
                # TODO heartbeat detected part
                else:
                    self.filled += line
        with open("test.md", "w") as file:
            file.write(self.filled)
        return self.filled

    def __str__(self):
        text = ""
        for elem in self.content:
            text += elem
        return text


# TODO API batch
def batch_answer():
    return


# TODO API
def answer():
    return



def test_answer(prompt):
    try:
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[{"role":"user", "content": prompt}],
            temperature = 0.5
        )
        with open(filename, "w") as out:
            out.write(response.choices[0].message.content)
            print(filename)
        return response.choices[0].message.content
    except OpenAIError as e:
        print(f'An error occurred: \n{e}')
        return "Error: " + e


def fake_answer(filename):
    template = Template(filename)
    return template.content


def list_to_text(l):
    txt = ""
    for e in l:
        txt += e
    return txt



if __name__ == "__main__":
    infected_template = Template("BERT/template/infected.md")
    safe_template = Template("BERT/template/safe.md")
    
    filled = infected_template.fill("../C2_prompt/data/csv/slimper/ls_kill.csv")

    
    candidates = [ filled ]
    answers = [ list_to_text(fake_answer("BERT/template/fake_answer.md")) ]

    warnings.simplefilter("ignore")

    P, R, F1 = score(candidates, answers, model_type='roberta-large', lang='en', verbose=False, rescale_with_baseline=True)

    print(f'Precision: {P.mean().item(): .4f}')
    print(f'Recall: {R.mean().item(): .4f}')
    print(f'F1: {F1.mean().item(): .4f}')