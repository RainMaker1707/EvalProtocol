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
    print(final_msg)
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
    parser.add_argument('-r', '--retrieve', action='store_true')
    parser.add_argument('-s', '--send', action='store_true')

    args = parser.parse_args()
    warnings.simplefilter("ignore")

    files_list = [
            "../data/json/slimper/full_local.json",
            "../data/json/slimper/idle.json",
            "../data/json/slimper/idle_ls_kill.json",
            "../data/json/slimper/ls_kill.json",
            "../data/json/new/httpbin.json",
            "../data/json/new/httpheanet.json",
            "../data/json/new/http.json",
        ]
    
    if not args.thread_id and not args.retrieve and not args.send:
        # in this case filename is the data file in the question in the thread. No response comes directly
        question = f'Analyze the file {args.filename.split("/")[-1]} to detect infection of Slimper C2 framework.'
        
        ID = answer(question)
        with open("thread_id.csv", "a") as file:
            file.write(f'I00007,{ID}\n')
        print(ID)  
    elif not args.retrieve and not args.send:
        # in this cas args.filename is the filename of the file containing a list of thread IDs
        ans = retrieve(args.thread_id)

        infected_template = Template("BERT/template/infected.md")
        safe_template = Template("BERT/template/safe.md")

        filled = infected_template.fill(args.filename)

        candidates = splitter(filled)
        answers = splitter(ans)

        P, R, F1 = score(candidates, answers, model_type='roberta-large', lang='en', verbose=False, rescale_with_baseline=True)

        print(f'Precision: {P}')
        print(f'Recall: {R}')
        print(f'F1: {F1}')

    elif args.thread_id and args.retrieve:
        print("Not implemented")

    elif not args.send and args.retrieve: # if not args.thread_id and args.recursive
        """
        # KEY pattern: I/S (infected or safe) 0-6 data file representation, 0-3 prompt ID, 0-5 Documentation version, 00-20 Temperature
        # Example: 
                - I02310 Infected ,file full_local.json, Prompt 2, Documentation 3, Temperature=1.0, 
                - S30105 Safe, file ls_kill.json, prompt 0, documentation 1, Temperature = 0.5 
        """
        df = pd.read_csv("BERT/thread_id.csv")
        threads_id_list = df["Value"].to_list()
        key_list = df["Key"].to_list()
        # Read and parse the saved thread_id
        for i in range(len(threads_id_list)):
            thread_id = threads_id_list[i]
            key = key_list[i]
            # retrieve thread answer.
            ans = retrieve(thread_id)
            # template part
            if "I" in key:
                template = Template("BERT/template/infected.md")
            else:
                template = Template("BERT/template/safe.md")
            filled = template.fill(files_list[int(key[1])])
            # score them
            candidates = splitter(filled)
            answers = splitter(ans)
            P, R, F1 = score(candidates, answers, model_type='roberta-large', lang='en', verbose=False, rescale_with_baseline=True)
            with open("BERT/json_score.csv", "a") as file:
                # TestID,ThreadID,HeadScoreP,HeadScoreR,HeadScore,F1,URLScoreP,URLScoreR,URLScoreF1,ExScoreP,ExScoreR,ExScoreF1 
                file.write('đ{key},{thread_id},{P[0]},{R[0]},{F1[0]},{P[1]},{R[1]},{F1[1]},{P[2]},{R[2]},{F1[2]}\n')
            print("Done " + i)

    elif args.send and not args.retrieve:
        print("here")
        idx = 0
        for filename in files_list:
            # in this case filename is the data file in the question in the thread. No response comes directly
            question = f'Analyze the file {filename.split("/")[-1]} to detect a potential infection of Slimper C2 framework.'
            
            ID = answer(question)
            with open("BERT/thread_id.csv", "a") as file:
                file.write(f'I{idx}0007,{ID}\n')
            idx += 1
            print(ID)  
