from openai import OpenAI
import config

client = OpenAI(api_key=config.key)

question1 = "Which method are used in this file? What are their purposes? On which URIs they relate? Is it a commonly see combination (method + URI)? My question is what can you deduce from a user perspective? Is it common HTTP traffic in the protocol perspective? What the user did? What the user browsed?"

question2 = "Which are the status code used? What are the request linked to these status code? What does mean each of these status code? What does mean these status code in term of user experience?"

question3 = "Which data are queried by the HTTP protocol? Does it seems legit browsing behavior? Does the method used correctly?"

question4 = "If you found parameters in URIs extracted, what do they refer to? What these parameters are used for? What does it means in term of user experience? (Prefer to say that you don't know instead of inventing things to answer.)"

questions = [question1, question2, question3, question4]

prompt = {
    "role": "I want you to act as a network analyst expert in HTTP(S) protocol.",
    "job": "Your job is to read a CSV file content user provides to answer the question below. This CSV file content is a wireshark sniff of the network and then it contains noise. You have to stick to HTTP(S) and related flux to answer. This CSV file content will be provided as plain text by the user, specified between [...] . Your answer should be based on your prior knowledge about HTTP(S)",
    "context": "The context is as follow: An enterprise take network data from their workers to watch if they work or procrastinate when at work. The csv content provided is a chunk of a network flow from one worker. Your job is not to check if they work or not but examine and summarize the HTTP packets in the network.",
}


with open("batchfile.jsonl", "r") as file:
    lines = list()
    batches = list()
    for i in range(1, 5):
        desc = f'evaluation F1 P1 Q{i}'
        filename = f'new_batch_p1q{i}.jsonl'
        used = questions[i-1]
        print(desc)

        for line in file.readlines():
            to_rep = "\"role\": \"system\", \"content\": \"\""
            rep =    "\"role\": \"system\", \"content\": \"" + prompt.get("job") + "\""  #+ prompt.get("context")
            new_line = line.replace(to_rep, rep)
            to_rep = "\"role\": \"user\", \"content\": \"\""
            rep =    "\"role\": \"user\", \"content\": \"" + used + "\""
            new_line = new_line.replace(to_rep, rep)
            lines.append(new_line)

        batch = "".join(lines)
        with open(filename, "w") as out:
            out.write(batch)

        batch = client.files.create(
                file=open(filename, "rb"),
                purpose="batch"
            )
        

        b = client.batches.create(
            input_file_id=batch.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": desc
            }
        )

        with open("batches.txt", "a") as log_file:
            log_file.write(str(b)+"\n\n")
    



