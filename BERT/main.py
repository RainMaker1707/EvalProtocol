from bert_score import score
import re
import pandas as pd
import json
import warnings
from openai import OpenAI, OpenAIError, ChatCompletion
import argparse
import numpy as np
from time import sleep



with open("BERT/configs/config.json", "r") as file:
    config = json.loads(file.read())
    file.close()


assistant_id = "asst_09zKFUlfy4UDUx7c5SCKg4Gq"
client = OpenAI(api_key=config.get("api_key"))



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
        if filename[-4:] == ".csv":
            df = pd.read_csv(filename)
            csv = df['request_uri'].dropna() 
            urls = csv.apply(lambda x: re.findall(r'\/[a-zA-Z._\-\/]+', x))
            urls = [e[0] for e in urls.to_list()]
            commands = [e for e in df['data'].dropna().to_list()]
            self.fill_default(urls, commands)
            # TODO heartbeat detected part 
   
        elif filename[-5:] == ".json":
            urls = []
            commands = []
            with open(filename, "r") as file:
                content = file.read()
                urls = re.findall(r'((\/[a-z]+){2,3}(\.[a-z]{2,4})?)+', content)
                commands = re.findall(r'(ls|kill)', content)
                file.close()
            urls = np.unique(np.array([e[0] for e in urls]))
            commands = np.unique(np.array(commands))
            self.fill_default(urls, commands)

        with open("test.md", "w") as file:
            file.write(self.filled)
        return self.filled


    def fill_default(self, urls, commands):
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
            else:
                self.filled += line

    def __str__(self):
        text = ""
        for elem in self.content:
            text += elem
        return text


# TODO API batch
def batch_answer():
    return

    

# TODO API
def answer(question):
    try:
        thread = client.beta.threads.create(
            messages=[{"role":"user", "content": question}]
        )
        print(thread.id)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        return thread.id
    except OpenAIError as e:
        print(f'An error occurred: \n{e}')
        sleep(60)
        return answer(question, thread_id)


def retrieve(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    final_msg = messages.data[0].content[0].text.value
    final_msg = final_msg[6:-4]
    return final_msg

def fake_answer(filename):
    template = Template(filename)
    return template.content


def list_to_text(l):
    txt = ""
    for e in l:
        txt += e
    return txt


def splitter(text):   
    if type(text) == type(list()):
        text = list_to_text(text)
    text_split = text.split('#')
    header = text_split[1]
    urls_part = text_split[3]
    commands_part = text_split[-1]
    return header, urls_part, commands_part



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-t', '--thread-id', type=str)

    args = parser.parse_args()
    
    if not args.thread_id:
        question = f'Analyze the file {args.filename.split("/")[-1]} to detect infection of Slimper C2 framework.'
        
        ID = answer(question)
        print(ID)  
    else:
        ans = retrieve(args.thread_id)

        infected_template = Template("BERT/template/infected.md")
        safe_template = Template("BERT/template/safe.md")

        filled = infected_template.fill(args.filename)

        candidates = splitter(filled)
        answers = splitter(ans)

        warnings.simplefilter("ignore")

        P, R, F1 = score(candidates, answers, model_type='roberta-large', lang='en', verbose=False, rescale_with_baseline=True)

        print(f'Precision: {P}')
        print(f'Recall: {R}')
        print(f'F1: {F1}')