from flask import Flask, request, redirect, render_template, flash, url_for, session, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
from run import PaperFinder
from item_analysis import get_item_analysis, get_response_analysis
import random, string
from csv_writer import write_csv



app = Flask(__name__)

UPLOAD_FOLDER = 'static/img'

app.config['SECRET_KEY'] = 'fucku'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_FILETYPES = ['png', 'jpeg', 'jpg']
SCORE = 0
current_file = ''
paper_finder = PaperFinder()
paper_finder.path = UPLOAD_FOLDER
item_analysis_data = {}
responses_analysis = {}
score = 0

def allowed_file(filename):
    split = filename.split(".")
    if split[1] in ALLOWED_FILETYPES:
        return True
    else:
        return False

def sort_dict(dict):
    dict = {key: dict[key] for key in sorted(dict, key=lambda a: int(a))}
    return dict

def generate_session_id():
    characterList = string.ascii_letters + string.digits
    sessionid = ''
    for i in range(5):
        randomchar = random.choice(characterList)
        sessionid += randomchar

    return sessionid

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()

    answerkey = session.get('answerkey', {})
    item_analysis_result = session.get('item_analysis_result', {})
    score = session.get('score')
    answers = session.get('answers', {})
    filename = session.get('current_file')

    return render_template('home.html', score=score, item_analysis_result=sort_dict(item_analysis_result), answerkey=sort_dict(answerkey), answers=answers, filename=filename)
    
@app.route('/download', methods=['GET', 'POST'])
def get_photo():
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], f"{session['session_id']}.jpg"), as_attachment=True)

@app.route('/', methods=['POST'])
def upload_img():
    if 'image' not in request.files:
        flash('No File Part')
        return redirect(request.url)
    
    file = request.files['image']
    print("Received file:", file.filename)

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)  

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print("Saving file to:", os.path.join(UPLOAD_FOLDER, filename))
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('File successfully uploaded')
        session['current_file'] = filename
        
        return redirect('/')
    else:
        flash('Allowed file types are .png, .jpg, .jpeg')
        return redirect(request.url)

@app.route('/check', methods=['POST'])
def check_paper():
    if 'current_file' in session:
        filename = session['current_file']
        print('checking', filename)
        # Check if answerkey is stored in session
        if 'answerkey' in session:
            session['answerkey'] = sort_dict(session['answerkey'])
            global score
            print('getting score')
            _, score = paper_finder.findpaper(os.path.join(UPLOAD_FOLDER, filename), session['answerkey'], session['session_id'])
            name = request.form.get('stud_name')
            if name:
                if 'stud_score' not in session:
                    session['stud_score'] = {}
                session['stud_score'][name] = score
                print(session['stud_score'])
            session['score'] = score

            # Perform item analysis
            if score is not None and score != -1:
                global item_analysis_data, responses_results
                answers, _ = paper_finder.findpaper(os.path.join(UPLOAD_FOLDER, filename), session['answerkey'], session['session_id'])
                item_analysis_result = get_item_analysis(answers, session['answerkey'], item_analysis_data)
                responses_results = get_response_analysis(answers, session['answerkey'], responses_analysis)
                if type(answers) is not int:
                    session['answers'] = answers

                session['item_analysis_result'] = item_analysis_result
                session['responses_result'] = responses_results
                sorted(session['answerkey'], key=lambda a: int(a))
                session['current_file'] = f"{session['session_id']}.jpg"
                # Pass item analysis result to home.html
                return redirect('/')
            else:
                flash('Error processing the paper.')
                return redirect('/')
        else:
            flash('Answer key not set.')
            return redirect('/')
    else:
        flash("No file")
        return redirect('/')    

@app.route('/answerkey')
def answerkey():
    if 'answerkey' in session:
        session['answerkey'] = sort_dict(session['answerkey'])
        return render_template('answer_key.html', answerkey=session['answerkey'])
    else:
        return render_template('answer_key.html')

@app.route('/answerkey', methods=['POST'])
def get_answer_key():
    answerkey = {}  # Print the entire form data to see what's being received
    if request.form:
        for key, value in request.form.items():
            print("Key:", key, "Value:", value)  # Print key-value pairs to check if they're correct
            if key.startswith('question'):
                question_num = int(key.replace('question', ''))
                answerkey[question_num] = value

        session['answerkey'] = answerkey
        print("Answer Key set in session:", session['answerkey'])  # Check if answer key is being set correctly

    return redirect('/')

@app.route('/reset')
def reset():
    global item_analysis_data, score
    item_analysis_data = {}
    session.pop('item_analysis_result')
    session.pop('score')

    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if 'responses_result' not in session:
        return render_template('responses.html')
    
    if request.method == 'POST' and 'download_csv' in request.form:
        write_csv(session['stud_score'], session['responses_result'], session['item_analysis_result'], session['session_id'])
        return send_file(f'{session["session_id"]}.csv', as_attachment=True)
    
    if request.method == 'POST' and 'reset_scores' in request.form:
        session.pop('stud_score')

    if request.method == 'POST' and 'reset_response' in request.form:
        session.pop('responses_result')

    stud_score = session.get('stud_score', {})
    responses_results = session.get('responses_result', {})
    
    return render_template('responses.html', responses=responses_results, stud_score=stud_score)


if __name__ == "__main__":
    app.run(debug=True)