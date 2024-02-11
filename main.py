from flask import Flask, request, redirect, render_template, flash, url_for, session
import os
from werkzeug.utils import secure_filename
from run import PaperFinder


app = Flask(__name__)

UPLOAD_FOLDER = 'static/img'

app.config['SECRET_KEY'] = 'fucku'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_FILETYPES = ['png', 'jpeg', 'jpg']
SCORE = 0
current_file = ''
paper_finder = PaperFinder()
paper_finder.path = UPLOAD_FOLDER

def allowed_file(filename):
    split = filename.split(".")
    if split[1] in ALLOWED_FILETYPES:
        return True
    else:
        return False

@app.route('/')
def home():
    paper_finder.score = 0
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
            score = 0
            paper_finder.findpaper(os.path.join(UPLOAD_FOLDER, filename))
            for i in range(len(session['answerkey'])):
                if paper_finder.answers[i] == session['answerkey'][str(i + 1)]:
                    score += 1
            session.pop('current_file')
            return render_template('home.html', filename=os.path.join('paperResults.jpg'), score=score)
        else:
            flash('Answer key not set.')
            return redirect('/')
    else:
        print('no file')
        return redirect('/')    

@app.route('/answerkey')
def answerkey():
    return render_template('answer_key.html')

@app.route('/answerkey', methods=['POST'])
def get_answer_key():
    answerkey = {}
    for key, value in request.form.items():
        if key.startswith('question'):
            question_num = key.replace('question', '')
            answerkey[question_num] = value
            print(answerkey)
    
    session['answerkey'] = answerkey

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)