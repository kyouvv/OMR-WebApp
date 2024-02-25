def get_Score(answers, answerkey):
    score = 0
    for i in range(len(answerkey)):
        if answers[i] == answerkey[str(i + 1)]:
            score += 1
                
    return score


def get_item_analysis(answers, answerkey, analysis):
    items = analysis

    for i in range(len(answerkey)):
        if i not in items:
            items[i] = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}

        if isinstance(answers, int):
            break
    
        if i < len(answers):
            if answers[i] == 'a':
                items[i]['a'] += 1
        
            if answers[i] == 'b':
                items[i]['b'] += 1

            if answers[i] == 'c':
                items[i]['c'] += 1

            if answers[i] == 'd':
                items[i]['d'] += 1

            if answers[i] == 'e':
                items[i]['e'] += 1

    return items

def get_response_analysis(answers, answer_key, responses):
    items = responses

    for i in range(len(answer_key)):
        print('creating', i)
        if i not in items:
            items[i] = {'correct': 0, 'incorrect': 0}  # Initialize correct and incorrect counts

        if isinstance(answers, int):
            break
    
        if i < len(answers):
            if answers[i] == answer_key[str(i + 1)]:  # Check if the answer is correct
                items[i]['correct'] += 1  # Increment correct count
            else:
                items[i]['incorrect'] += 1  # Increment incorrect count

    return items
