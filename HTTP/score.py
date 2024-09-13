def score(good_answers, bad_answers, hallucinations):
    N = good_answers + bad_answers + hallucinations
    w0 = 1
    w1 = 0
    w2 = -.2
    return w0 *(good_answers/N) + w1 * (bad_answers/N) + w2 *(hallucinations/N)

def test_score(n=10):
    triplets = dict()
    for i in range(n+1):
        for j in range(n+1):
            for h in range(n+1):
                if i + j + h != n:
                    pass
                else:
                    triplets[(i, j, h)] = (i, j, h)
    scores = dict()
    for key in triplets.keys():
        var =  triplets.get(key)
        scores[key] = score(var[0], var[1], var[2]) 
    
    #plot scores
    return scores



def score_file():
    return


if __name__ == "__main__":
    scores = test_score()
    print(scores)
    print(len(scores))