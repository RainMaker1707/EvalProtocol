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
    
with open("BERT/dictionaries.json", "r") as file:
    dictionaries = json.loads(file.read())
    file.close()


PROMPT_ID = 3
prompt_id = PROMPT_ID
temp = 5


client = OpenAI(api_key=config.get("api_key"))

assistant_id = "asst_H901WiVOTk7IrrejU2hQM22j"

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
                final = list()
                for url in urls:
                    if self.is_slimper_url(url[0]):
                        final.append(url)
                urls = final
                commands = re.findall(r'(ls|kill)', content)
                file.close()
            urls = np.unique(np.array([e[0] for e in urls]))
            commands = np.unique(np.array(commands))
            self.fill_default(urls, commands)

        with open("test.md", "w") as file:
            file.write(self.filled)
        return self.filled

    def is_slimper_url(self, url):
        # URL as two to three parts
        if len(url.split("/")) < 2 or len(url.split('/')) > 3: 
            return False
        # URL finish with no extension or .js / .png 
        poll_paths = dictionaries.get("poll_paths")
        paths = dictionaries.get("paths")
        kill_paths = dictionaries.get("kill_paths")
        

        poll_files = dictionaries.get("poll_files")
        files = dictionaries.get("files")
        kill_files = dictionaries.get("kill_files")

        splitted = url.split("/")[1:]

        if not splitted[0] in poll_paths + paths + kill_paths:
            return False
        if not splitted[1] in [f'{e}.js' for e in poll_files] + files + [f'{e}.png' for e in kill_files]:
            return False
        return True


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
    print(text)
    if type(text) == type(list()):
        text = list_to_text(text)
    text_split = text.split('#')
    header = text_split[1]
    urls_part = text_split[3]
    commands_part = text_split[-1]
    return [header, urls_part, commands_part]



def filter(ls, pat):
    nl = list()
    for e in ls:
        if e != pat:
            nl.append(e)
    return nl

def filter_none(ls):
    nl = list()
    for e in ls:
        if not ("None" in e) and not ("[]" in e) and not ("[ ]" in e):
            nl.append(e)
    return nl

"""
This function will return a score based on how many urls in the answer are in the templates too.
But if we just count the url present in ans the score will be biaised as the answer can contains all possibilities to achieve a perfect score.
N: The number of good unique URLs in both urls and ans.
T1: The total of URLs in urls.
T2: The total of URLs in the answer.
S = T/((T1+T2)/2) 
If the answer is perfect it has the same len as the urls list. then (T1 + T2)/2 = T1 = T2 and if all urls are good T = T1 = T2
-> It ensures the score to reaches S = 1
If T2 is greater than T1 then at least one urls is false, same if all the other are good the score will decrease.
-> T = T1 < T2 --> S < 1
If T1 is greater than T2, at least one URLs is missing then T < T1 --> S < 1
If no URL matches then T = 0 and the score reach 0
-> 0 / ((T1+T2)/2) with T1 et T2 random positive and different then S = 0.

If T1 = T2 = 0 then S = 1
If T1 = 0 and T1 != T2 then S = 0
As T1 and T2 are len Dom(T1) = Dom(T2) = [0, +inf] 

"""
def url_score(urls, ans, test_id="I00000"):
    urls = urls[15:].split("\n")
    urls = [ u.replace("\t- ", "") for u in urls ]
    ans = ans[15:].split("\n")
    urls = filter(urls, '')
    ans = filter_none(filter(ans, ''))
    print("URL: ", urls)
    print("ANS: ", ans)
    T = 0
    T1 = len(urls)
    T2 = len(ans)
    if T1 == 0 and T2 == 0:
        return 1.0, 1.0, 1.0
    elif (T1 == 0 and T2 != 0) or (T1 != 0 and T2 == 0):
        return 0.0, 0.0, 0.0
    else:
        matched = dict()
        for u in urls:
            for e in ans:
                if u in e and not u in matched.keys():
                    T += 1
                    matched[u] = T
        UT, UT1, UT2 = T / ((T1+T2)/2), T/T1, T/T2
        return UT, UT1, UT2


def head_score(a, b):
    if "infected" in a and "infected" in b:
        return 1.0
    if "safe" in a and "safe" in b:
        return 1.0
    return 0.0



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--retrieve', action='store_true')
    parser.add_argument('-o', '--output', type=str, required=True)

    parser.add_argument('-i', '--input-file', type=str)
    
    parser.add_argument('-c', '--custom', action='store_true')
    parser.add_argument('-p', '--prompt', type=int)
    parser.add_argument('-f', '--file', type=int)
    parser.add_argument('-t', '--temp', type=float)
    parser.add_argument('-n', '--number-of-test', type=int)

    parser.add_argument('-s', '--score-test', action='store_true')
    args = parser.parse_args()
    warnings.simplefilter("ignore")

    files_list = [
            "../data/json/slimper/full_local.json",
            "../data/json/slimper/idle.json",
            "../data/json/slimper/idle_ls_kill.json",
            "../data/json/slimper/ls_kill.json",
            "../data/json/new/httpbin.json",
            "../data/json/new/http.json",
            # "../data/json/new/httpheanet.json"
        ]
    
    

    if args.retrieve and args.custom:
        print("Error incompatible option retrieve and custom.")
        exit(1)

    elif args.retrieve:
        if not args.input_file:
            print("Input file required.")
            exit(1)
        """
        # KEY pattern: I/S (infected or safe) 0-6 data file representation, 0-3 prompt ID, 0-5 Documentation version, 00-20 Temperature
        # Example: 
                - I02310 Infected ,file full_local.json, Prompt 2, Documentation 3, Temperature=1.0, 
                - S30105 Safe, file ls_kill.json, prompt 0, documentation 1, Temperature = 0.5 
        """
        df = pd.read_csv(args.input_file)
        threads_id_list = df["Value"].to_list()
        key_list = df["Key"].to_list()
        print("key, value retrieved")
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
            try:
                candidates = splitter(filled)
                answers = splitter(ans)
                print(answers[0])
                UN, UT1, UT2 = url_score(candidates[1], answers[1], test_id=key)
                print(UN, "\n", UT1, "\n", UT2)
                try:
                    P, R, F1 = score(candidates, answers, model_type='roberta-large', lang='en', verbose=False, rescale_with_baseline=True)
                    with open(args.output, "a") as file:
                        # TestID,ThreadID,HeadScoreP,URLScoreP,URLScoreR,URLScoreF1,ExScoreP,ExScoreR,ExScoreF1,UN,UT1,UT2 
                        file.write(f'{key[0]},{key[1]},{key[2]},{key[3]},{key[4]}.{key[5]},{thread_id},{head_score(candidates[0], answers[0])},{P[2]:.3f},{R[2]:.3f},{F1[2]:.3f},{UN:.3f},{UT1:.3f},{UT2:.3f}\n')
                except:
                    print("Error in splitter for thread: " + thread_id + ", file: " + key)
            except:
                print(thread_id)


    elif args.custom:
        print(f'Pid: {args.prompt}')
        print(f'Fid: {args.file}')
        print(f'Temp: {args.temp}')
        print(f'N: {args.number_of_test}')
        print(f'Out: {args.output}')
        arg_check = True
        if not args.prompt and not args.prompt == 0:
            print("Require prompt id (one digit int).")
            arg_check = False
        if not args.file and not args.file == 0:
            print("Required file id (one digit int).")
            arg_check = False
        if not args.number_of_test or args.number_of_test < 1:
            print("Required number of test (positive non nul int)")
            arg_check = False
        if not args.temp:
            print("Required temperature to use (float 2 digits (0.5), [0.1, 2])")
            arg_check = False
        if not arg_check:
            exit(1)
            
        filename = files_list[args.file]
        state = "I" if 'slimper' in filename else "S"
        encode_test_id = f'{state}{args.file}{args.prompt}0{int(args.temp*10):02d}'
        print(f'TestID: {encode_test_id}')

        vector = "vs_UiEEoktDa6dFPU4MFhcsBUDF"
        question =  f'Analyze the file {args.file}.json file stored in the vector {vector} to detect a potential infection.'

        for i in range(args.number_of_test):
            
            thread_id = answer(question)
            sleep(10)
            with open(args.output, "a") as file:
                file.write(f'{encode_test_id},{thread_id}\n')
                file.close()
        print("All done")
        


    elif args.score_test:
        from random import choices

        urls = ['/abc/123', '/azeeert/ézaeavez123', '/erte/aeeev/123', '/ert/3453/ced', '/ert/1234/ced', '/abc/124', '/azeeer2t/ézaeavez123', '/erte/a2eeev/123', '/ert/34523/ced', '/ert/12234/ced']
        with open(args.output, 'w+') as file:
            file.write("T, T1, T2, UT, UT1, UT2\n")
            file.close()
        for i in range(args.number_of_test):
            ans = choices(urls, k=i%(int(len(urls)*1.5)))
            T = 0
            T1 = len(urls)
            T2 = len(ans)
            if T1 == 0 and T2 == 0:
                with open(args.output, 'a') as file:
                    file.write(f'{T},{T1},{T2},1.0,1.0,1.0\n')
                    file.close()
            elif (T1 == 0 and T2 != 0) or (T1 != 0 and T2 == 0):
                with open(args.output, 'a') as file:
                    file.write(f'{T},{T1},{T2},0.0,0.0,0.0\n')
                    file.close()
            else:
                matched = dict()
                for u in urls:
                    for e in ans:
                        if u in e and not u in matched.keys():
                            T += 1
                            matched[u] = T
                UT, UT1, UT2 = T / ((T1+T2)/2), T/T1, T/T2
                with open(args.output, 'a') as file:
                    file.write(f'{T},{T1},{T2},{UT},{UT1},{UT2}\n')
                    file.close()
        print("All done")


    else:
        print("Not recognized arguments.")