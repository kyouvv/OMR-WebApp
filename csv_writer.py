import csv

def get_score_mean(scores):
    totalScore = 0
    for name, score in scores.items():
        totalScore += score
    
    totalScore = totalScore/len(scores)
    return totalScore    

def write_csv(scores, responses, item_analysis, session_id):
    print('Writing CSV...')
    with open(f'{session_id}.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, score in scores.items():
            writer.writerow({'Name': name, 'Score': score})
        mean = get_score_mean(scores)
        writer.writerow({'Name' : 'Mean Score', 'Score': mean})
        
        fieldnames = ['Question', 'Correct', 'Incorrect']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for question_num, data in responses.items():
            writer.writerow({'Question': question_num, 'Correct': data['correct'], 'Incorrect': data['incorrect']})
        
        fieldnames = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Option E']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for question, options in item_analysis.items():
            option_counts = {f'Option {key.upper()}': value for key, value in options.items()}
            writer.writerow({'Question': question, **option_counts})
