from openai import OpenAI, OpenAIError
import pandas as pd
from time import sleep
import config


client = OpenAI(api_key=config.key)



def ask(prompt, question, filename):
    try:
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[{"role":"system", "content": prompt}, {"role":"user", "content": question}],
            temperature = 0.5
        )
        with open(filename, "w") as out:
            out.write(response.choices[0].message.content)
            print(filename)
        return response.choices[0].message.content
    except OpenAIError as e:
        print(f'An error occurred: \n{e}')
        sleep(10*60)
        return ask(prompt, question, filename)


prompts= {
    "role": "I want you to act as a network analyst expert in HTTP(S) protocol.",
    "job": "Your job is to read a CSV file content user provides to answer the question below. This CSV file content is a wireshark sniff of the network and then it contains noise. You have to stick to HTTP(S) and related flux to answer. This CSV file content will be provided as plain text by the user, specified between \"[...]\" . Your answer should be based on your prior knowledge about HTTP(S)",
    "context": "The context is as follow: An enterprise take network data from their workers to watch if they work or procrastinate when at work. The csv content provided is a chunk of a network flow from one worker. Your job is not to check if they work or not but examine and summarize the HTTP packets in the network.",
}


def preprocess(file):
    df = pd.read_csv(file)
    http_requests = df[df['protocol'] == "HTTP"]
    IPs = http_requests['source'].unique().tolist()
    http_requests.to_csv("heanet_extract.csv")


def combinations(IPs):
    pass


if __name__ == "__main__":
    preprocess("./tests/HTTP/sample/httpheanet.csv")
    question1 = """
                    Which method are used in this file? What are their purposes? 
                    On which URIs they relate? Is it a commonly see combination (method + URI)?
                    My question is what can you deduce from a user perspective?
                    Is it common HTTP traffic in the protocol perspective?
                    What the user did?
                    What the user browsed?
                """

    question2 = """
                    Which are the status code used? What are the request linked to these status code? 
                    What does mean each of these status code?
                    What does mean these status code in term of user experience?
                """

    question3 = """
                    Which data are queried by the HTTP protocol?
                    Does it seems legit browsing behavior?
                    Does the method used correctly?
                """

    question4 = """
                    If you found parameters in URIs extracted, what do they refer to?
                    What these parameters are used for?
                    What does it means in term of user experience?
                    (Prefer to say that you don't know instead of inventing things to answer.)
                """


    questions = [question1, question2, question3, question4]
    answers = list()
    question_start = 1
    i_start = 0
    file_content = ""
    with open("heanet_extract.csv", "r") as file:
        file_content = file.read()
    if file_content == "":
        print("error reading file")
        exit(1)
    for q in range(len(questions)):
        if q < question_start - 1: 
            pass
        else:
            for i in range(10):
                if q == question_start - 1 and i < i_start:
                    pass
                else:
                    print(q+1, ":", i)
                    question = f'Here is the CSV file content: "{file_content}". My request is {questions[q]}'
                    prompt = prompts.get("role") + prompts.get("job") + prompts.get("context")
                    ask(prompt, question, f'tests/HTTP/results/P3Q{q+1}_{i}.txt')
                    sleep(60)
                