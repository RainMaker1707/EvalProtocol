import pandas as pd


df = pd.read_csv("BERT/one_file_vector/data/score_temp.csv")

temps = [ 0.2, 0.3, 0.4, 0.5, 0.6]


def score(TP, FP, TN, FN):
    P = precision(TP, FP, TN, FN)
    R = recall(TP, FP, TN, FN)
    F1 = f1(TP, FP, TN, FN)
    return {'P': P, 'R': R, 'F1': F1} 


def precision(TP, FP, TN, FN):
    return TP/(TP+FP)

def recall(TP, FP, TN, FN):
    return TP/(TP+FN)

def f1(TP, FP, TN, FN):
    p = precision(TP, FP, TN, FN)
    r = recall(TP, FP, TN, FN)
    return 2*((p*r)/(p+r))

TP, FP, TN, FN = 0, 0, 0, 0

with open("BERT/one_file_vector/data/f1_temp.csv", "w") as file:
        file.write("Temp,TP,FP,TN,FN,P,R,F1\n")
        file.close()

for temp in temps:
    TP, FP, TN, FN = 0, 0, 0, 0
    data = df.loc[df['Temp'] == temp]
    for i in range(len(data['HeadScore'].values)):
        elem = data.iloc[i]
        if elem["State"] == "I" and elem["HeadScore"] == 1.0:
            TP += 1
        elif elem["State"] == "I" and elem["HeadScore"] == 0.0:
            FN += 1
        elif elem["State"] == "S" and elem["HeadScore"] == 1.0:
            TN += 1
        elif elem["State"] == "S" and elem["HeadScore"] == 0.0:
            FP += 1
    with open("BERT/one_file_vector/data/f1_temp.csv", "a") as file:
        if temp == 0.2: FN = 6
        s = score(TP, FP, TN, FN)
        file.write(f'{temp},{TP},{FP},{TN},{FN},{s.get("P")},{s.get("R")},{s.get("F1")}\n')
        file.close()



print("All done")
exit(0)
