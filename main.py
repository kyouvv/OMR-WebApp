from flask import Flask, request, redirect, render_template, flash, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
from run import PaperFinder
from item_analysis import get_item_analysis



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
score = 0

def allowed_file(filename):
    split = filename.split(".")
    if split[1] in ALLOWED_FILETYPES:
        return True
    else:
        return False

@app.route('/')
def home():
    if 'item_analysis_result' in session and 'answerkey' in session and 'score' in session:
        return render_template('home.html',score=score, item_analysis_result=session['item_analysis_result'], answerkey=session['answerkey'])
    if 'item_analysis_result' in session and 'answerkey' in session:
        return render_template('home.html', item_analysis_result=session['item_analysis_result'], answerkey=session['answerkey'])
    if 'answerkey' in session:
        return render_template('home.html', answerkey=session['answerkey'])
    else:
        print('none exists')
        return render_template('home.html')

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
        if 'answerkey' in session:
            return render_template('home.html', answerkey=session['answerkey'], filename=filename)
        if 'item_analysis_result' in session and 'answerkey' in session and 'score' in session:
            return render_template('home.html', score=session['score'], item_analysis_result=session['item_analysis_result'], answerkey=session['answerkey'], filename=filename)
        if 'item_analysis_result' in session and 'answerkey' in session:
            return render_template('home.html', item_analysis_result=session['item_analysis_result'], answerkey=session['answerkey'])
        return render_template('home.html', filename=filename)
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
            print('answer key exists')
            global score
            print('getting score')
            _, score = paper_finder.findpaper(os.path.join(UPLOAD_FOLDER, filename), session['answerkey'])
            print(score)
            session['score'] = score

            # Perform item analysis
            if score is not None and score != -1:
                global item_analysis_data
                answers, _ = paper_finder.findpaper(os.path.join(UPLOAD_FOLDER, filename), session['answerkey'])
                item_analysis_result = get_item_analysis(answers, session['answerkey'], item_analysis_data)

                session['item_analysis_result'] = item_analysis_result

                # Pass item analysis result to home.html
                return render_template('home.html', filename=os.path.join('paperResults.jpg'), score=session['score'], item_analysis_result=session['item_analysis_result'], answerkey=session['answerkey'])
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
        answerkey = session['answerkey']
        return render_template('answer_key.html', answerkey=answerkey)
    else:
        return render_template('answer_key.html')

@app.route('/answerkey', methods=['POST'])
def get_answer_key():
    answerkey = {}
    if request.form:
        for key, value in request.form.items():
            if key.startswith('question'):
                question_num = int(key.replace('question', ''))
                answerkey[question_num] = value

        session['answerkey'] = answerkey

    return redirect('/')

@app.route('/reset')
def reset():
    global item_analysis_data, score
    session.pop('item_analysis_result')
    session.pop('score')

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)