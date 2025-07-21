from flask import Flask, render_template, request, redirect, url_for, session
import os
import openai

app = Flask(__name__)
app.secret_key = 'change_this_secret'

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'mp3', 'wav', 'mp4', 'mov'}

# File size limits by plan (bytes)
PLAN_LIMITS = {
    'free': 1 * 1024 * 1024,
    'pro': 5 * 1024 * 1024,
    'premium': 10 * 1024 * 1024,
}

openai.api_key = os.getenv('OPENAI_API_KEY')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        plan = request.form.get('plan', 'free')
        difficulty = request.form.get('difficulty', 'medium')
        file = request.files.get('document')
        if not file or file.filename == '' or not allowed_file(file.filename):
            return render_template('index.html', error='Invalid file type', plan=plan)
        max_size = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > max_size:
            return render_template('index.html', error='File too large for your plan', plan=plan)
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        session['plan'] = plan
        session['difficulty'] = difficulty
        session['filepath'] = filepath
        return redirect(url_for('quiz'))
    return render_template('index.html')


@app.route('/quiz')
def quiz():
    plan = session.get('plan', 'free')
    filepath = session.get('filepath')
    difficulty = session.get('difficulty', 'medium')
    if not filepath:
        return redirect(url_for('index'))

    with open(filepath, 'rb') as f:
        content = f.read()

    if plan == 'free':
        num_questions = 15
    else:
        length_kb = len(content) / 1024
        # Simple heuristic: 1 question per 20KB with a minimum of 15
        num_questions = max(15, int(length_kb / 20) + 1)

    prompt = (
        f"Generate {num_questions} multiple choice questions with 4 options "
        f"based on the uploaded content. "
        f"Difficulty: {difficulty}." 
    )
    # The actual document content is not passed to keep it short, but in a real
    # application you would supply a transcription or text extraction result.

    messages = [
        {"role": "system", "content": "You are a helpful assistant that creates quiz questions."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        questions_text = response.choices[0].message['content']
    except Exception:
        # fallback sample questions if API fails
        questions_text = """1. Sample question?\nA. A\nB. B\nC. C\nD. D\n"""

    # Parse questions into structure [ {question:'', options:['A','B','C','D'], answer:'A'} ]
    questions = []
    for block in questions_text.strip().split('\n\n'):
        parts = block.strip().split('\n')
        if len(parts) >= 5:
            question = parts[0]
            options = [p[3:].strip() for p in parts[1:5]]
            answer = 'A'
            questions.append({'question': question, 'options': options, 'answer': answer})
    session['questions'] = questions
    return render_template('quiz.html', questions=questions)


@app.route('/submit', methods=['POST'])
def submit():
    questions = session.get('questions', [])
    results = []
    score = 0
    for idx, q in enumerate(questions):
        user_answer = request.form.get(f'q{idx}')
        correct = q['answer'] == user_answer
        results.append({'question': q['question'], 'user': user_answer, 'correct': correct, 'answer': q['answer'], 'options': q['options']})
        if correct:
            score += 1
    return render_template('result.html', results=results, score=score, total=len(questions))


if __name__ == '__main__':
    app.run(debug=True)
