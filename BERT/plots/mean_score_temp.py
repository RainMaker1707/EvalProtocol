
"""
This file will contain a mean score plot script from the file json_score_temp.csv
It will print the mean for each temp and the mean for each (temp, file) pair
The data file contain score for each configuration of each file with the three temperatures 0.5, 0.7, 1.0
with three runs per configuration to compute the mean

Configuration codage (TestID column in csv)
I/S (infected or safe) 0-6 data file representation, 0-3 prompt ID, 0-5 Documentation version, 00-20 Temperature
Example: 
        - I02310 Infected ,file full_local.json, Prompt 2, Documentation 3, Temperature=1.0, 
        - S30105 Safe, file ls_kill.json, prompt 0, documentation 1, Temperature = 0.5 
""" 


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from argparse import ArgumentParser


files_list = [
                "../data/json/slimper/full_local.json",
                "../data/json/slimper/idle.json",
                "../data/json/slimper/idle_ls_kill.json",
                "../data/json/slimper/ls_kill.json",
                "../data/json/new/httpbin.json",
                "../data/json/new/http.json",
                # "../data/json/new/httpheanet.json"
        ]

def decode(configuration):
        decoded = {
                "infected": True if "I" == configuration[0] else False,
                "fileID": int(configuration[1]),
                "promptID": int(configuration[2]),
                "docID": int(configuration[3]),
                "temperature": int(configuration[4:])/10
        }
        return decoded


def fileID_to_filename(id):
        return files_list[id]


def parse_data(filename, save=True, output_name="out", temp=True):
        df = pd.read_csv(filename)
        data = list()
        idx = 0
        for _ in df["TestID"]:
                data.append(df.iloc[idx].to_dict())
                idx += 1
        save_file(data, output_name, temp)
        return data


def get_all_same_temp(dictionaries, temp):
        data = list()
        for elem in dictionaries:
                if np.isclose(decode(elem.get('TestID')).get("temperature"), temp/10):
                        data.append(elem)
        return data
        
def get_all_infected(dictionaries):
        data = list()
        for elem in dictionaries:
                if "I" in elem.get('TestID'):
                        data.append(elem)
        return data

def mean_head_score(test):
        means = {
                "HeaderP": np.mean([1 if e.get('HeadScoreP') == 1.0 else 0 for e in test]),
                "HeaderR": np.mean([1 if e.get('HeadScoreR') == 1.0 else 0 for e in test]),
                "HeaderF1": np.mean([1 if e.get('HeadScoreF1') == 1.0 else 0 for e in test]),
                "UP": np.mean([e.get('URLScoreP') for e in test]),
                "UR": np.mean([e.get('URLScoreR') for e in test]),
                "UF1": np.mean([e.get('URLScoreF1') for e in test]),
                "UN": np.mean([e.get('URLNewScore') for e in test]),
                "UT1": np.mean([e.get('UT1') for e in test]),
                "UT2": np.mean([e.get('UT2') for e in test])
        }
        return means


def save_file(data, output_name, p):
        with open(f'BERT/data/{output_name}.csv', "w") as file:
                file.write("PromptID,Temp,HP,HR,HF1,UP,UR,UF1,UN,UT1,UT2\n")
                for prompt_id in range(3):
                        for temp in [5, 7, 10]:
                                split = get_all_same_temp(data, temp)
                                if len(split) > 0:
                                        means = mean_head_score(split)
                                        P, R, F1 = means.get('HeaderP'), means.get("HeaderR"), means.get('HeaderF1')
                                        UP, UR, UF1 = means.get('UP'), means.get('UR'), means.get('UF1')
                                        UN, UT1, UT2 = means.get('UN'), means.get('UT1'), means.get('UT2')
                                        file.write(f'{prompt_id},{temp/10},{P},{R},{F1},{UP},{UR},{UF1},{UN},{UT1},{UT2}\n')


def graph_temp(save=True):
        ### Plotting
        df = pd.read_csv("BERT/data/result_temp.csv")
        
        temperatures = [0.5, 0.7, 1.0]
        y = {
                "Precision": [float(f'{e:.2f}') for e in df["HP"][0:3].values],
                "Recall": [float(f'{e:.2f}') for e in df['HR'][0:3].values],
                "F1": [float(f'{e:.2f}') for e in df['HF1'][0:3].values],
        }
        title = 'Header BERT scores against temperature for prompt 0'
        draw_bar_chart(temperatures, y, title, 'Header scores', save=save)

        y = {
                "Precision": [float(f'{e:.2f}') for e in df["HP"][3:6].values],
                "Recall": [float(f'{e:.2f}') for e in df['HR'][3:6].values],
                "F1": [float(f'{e:.2f}') for e in df['HF1'][3:6].values],
        }
        title = 'Header BERT scores against temperature for prompt 1'
        draw_bar_chart(temperatures, y, title, 'Header scores', save=save)

        y = {
                "Precision": [float(f'{e:.2f}') for e in df["HP"][6:9].values],
                "Recall": [float(f'{e:.2f}') for e in df['HR'][6:9].values],
                "F1": [float(f'{e:.2f}') for e in df['HF1'][6:9].values],
        }
        title = 'Header BERT scores against temperature for prompt 2'
        draw_bar_chart(temperatures, y, title, 'Header scores', save=save)

        y2 = {
                "URL Precision":[float(f'{e:.2f}') for e in df['UP'][0:3].values],
                "URL Recall": [float(f'{e:.2f}') for e in df['UR'][0:3].values],
                "URL F1": [float(f'{e:.2f}') for e in df['UF1'][0:3].values],
                "URL new score": [float(f'{e:.2f}')for e in df['UN'][3:6].values] 
        }
        title = 'URL BERT scores against temperature for prompt 0'
        draw_bar_chart(temperatures, y2, title, 'URL scores', limit=1.1, save=save)

        y2 = {
                "URL Precision":[float(f'{e:.2f}') for e in df['UP'][3:6].values],
                "URL Recall": [float(f'{e:.2f}') for e in df['UR'][3:6].values],
                "URL F1": [float(f'{e:.2f}') for e in df['UF1'][3:6].values],
                "URL new score": [float(f'{e:.2f}')for e in df['UN'][3:6].values] 
        }
        title = 'URL BERT scores against temperature for prompt 1'
        draw_bar_chart(temperatures, y2, title, 'URL scores', limit=1.1, save=save)

        y2 = {
                "URL Precision": [float(f'{e:.2f}')for e in df['UP'][3:6].values],
                "URL Recall": [float(f'{e:.2f}')for e in df['UR'][3:6].values],
                "URL F1 score": [float(f'{e:.2f}')for e in df['UF1'][3:6].values],
                "URL new score": [float(f'{e:.2f}')for e in df['UN'][3:6].values]
        }
        title = 'URL BERT against temperature for prompt 2'
        draw_bar_chart(temperatures, y2, title, 'URL scores', limit=1.1, save=save)


def graph_prompt(save=True):
        df = pd.read_csv("BERT/data/result_temp.csv")
        data = parse_data("BERT/data/json_score_prompt3.csv", output_name="result_prompt3")
        df2 = pd.read_csv("BERT/data/result_prompt3.csv")

        labels = ["Prompt 0", "Prompt 1", "Prompt 2", "Prompt 3"]
        y = {
                "Precision": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['HP'].values] + [np.mean(df2['HP'].values)],
                "Recall": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['HR'].values] + [np.mean(df2['HR'].values)],
                "F1 score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['HF1'].values] + [np.mean(df2['HF1'].values)],
        }
        draw_bar_chart(labels, y, 'Header BERT scores of the different prompts', 'Score', low= 0.5, limit=1.1, n=4, save=save)
        
        y = {
                "URL Precision": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UP'].values] + [np.mean(df2['UP'].values)],
                "URL Recall": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UR'].values] + [np.mean(df2['UR'].values)],
                "URL F1 score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UF1'].values] + [np.mean(df2['UF1'].values)],
                "URL new score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UN'].values] + [np.mean(df2['UN'].values)] 
        }
        draw_bar_chart(labels, y, "URL BERT scores for the different prompts", 'Score', limit=1.1, n=4, save=save)


def graph_new_score(save=True):
        df = pd.read_csv("BERT/data/result_temp.csv")
        data = parse_data("BERT/data/json_score_prompt3.csv", output_name="result_prompt3")
        df2 = pd.read_csv("BERT/data/result_prompt3.csv")
        labels = ["Prompt 0", "Prompt 1", "Prompt 2", "Prompt 3"]
        y = {
                "URL New score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UN'].values] + [np.mean(df2['UN'].values)],
                "URL T1 score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UT1'].values] + [np.mean(df2['UT1'].values)],
                "URL T2 score": [float(f'{e:.2f}')for e in df.loc[df["Temp"] == 0.5]['UT2'].values] + [np.mean(df2['UT2'].values)] 
        }
        draw_bar_chart(labels, y, "URL scores for the different prompts T=0.5", 'Score', limit=1.1, n=4, save=save)


        

def draw_bar_chart(labels, y, title, y_label, low=0, limit=1.0, save=True, n=3):
        x = np.arange(n)
        width = 0.15  # the width of the bars
        multiplier = 0

        fig, ax = plt.subplots(layout='constrained')

        for attribute, measurement in y.items():
                offset = width * multiplier
                rectangle = ax.bar(x + offset, measurement, width, label=attribute)
                ax.bar_label(rectangle, padding=5)
                multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.set_xticks(x + width, labels)
        ax.legend(loc='upper left', ncols=3)
        ax.set_ylim(low, limit)
        if save:
                plt.savefig(f'BERT/plots/outputs/{title}.pdf', format="pdf")




if __name__ =="__main__":
        parser = ArgumentParser()
        parser.add_argument("filename")

        args = parser.parse_args()

        print("Plotting...")

        data = parse_data(args.filename, output_name="result_temp")
        graph_temp(True)
        graph_prompt(True)
        graph_new_score(True)
        plt.show()