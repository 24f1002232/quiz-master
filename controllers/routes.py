from app import app
from flask import render_template, request, redirect, session, url_for, flash
from controllers.models import *
import io
import base64
import statistics
from datetime import datetime
import matplotlib
# Use non-interactive backend for server-side PNG generation
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user1 = User.query.filter_by(email=email).first()

        if not user1:
            flash('User not found')
            return redirect(url_for('register'))
        # verify hashed password
        if not check_password_hash(user1.password, password):
            flash('Incorrect password')
            return render_template('login.html')

        session['user_email'] = user1.email
        session['role'] = user1.role
        session['name'] = user1.name

        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')
        qualification = request.form.get('qualification')

        if password != confirm_pass:
            flash('Passwords do not match')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('User already exists')
            return render_template('register.html')

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            qualification=qualification,
            role="user"
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration Successful!, Login in to continue')
        return redirect(url_for('login'))


@app.route('/manage_users')
def manage_users():
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    users = User.query.filter_by(role="user").all()
    return render_template('manage_users.html', users=users)


@app.route('/delete_user/<int:id>')
def delete_user(id):
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))

    user = User.query.filter_by(id=id).first()
    if not user:
        flash('User not found')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()

    flash('User deleted Successfully! ')
    return redirect(url_for('manage_users'))


@app.route('/manage_subject')
def manage_subject():
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    return render_template('manage_subject.html')


# ------------------ Matplotlib analysis helpers & routes ------------------

def _generate_image_bytes_from_figure(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return data


@app.route('/quiz/<int:quiz_id>/analysis')
def quiz_analysis(quiz_id):
    # Admin-only
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))

    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        flash('Quiz not found')
        return redirect(url_for('home'))

    attempts = Score.query.filter_by(quiz_id=quiz_id).order_by(Score.time).all()
    if not attempts:
        flash('No attempts for this quiz yet')
        return render_template('analysis_quiz.html', quiz=quiz, chart_data=None, stats=None, attempts=[])

    scores = [a.score for a in attempts]
    stats = {}
    stats['count'] = len(scores)
    try:
        stats['mean'] = round(statistics.mean(scores), 2)
        stats['median'] = round(statistics.median(scores), 2)
    except statistics.StatisticsError:
        stats['mean'] = stats['median'] = None
    stats['min'] = min(scores)
    stats['max'] = max(scores)

    # Histogram
    fig = plt.figure(figsize=(6, 4))
    bins = min(10, max(1, len(set(scores))))
    plt.hist(scores, bins=bins, color='skyblue', edgecolor='black')
    plt.xlabel('Score')
    plt.ylabel('Count')
    plt.title(f'Score Distribution for {quiz.name}')

    chart_data = 'data:image/png;base64,' + _generate_image_bytes_from_figure(fig)

    # Build attempt rows with user names
    attempt_rows = []
    for a in attempts:
        user = User.query.filter_by(id=a.user_id).first()
        attempt_rows.append({'user': user.name if user else 'Unknown', 'score': a.score, 'time': a.time})

    return render_template('analysis_quiz.html', quiz=quiz, chart_data=chart_data, stats=stats, attempts=attempt_rows)


@app.route('/my_analysis')
def my_analysis():
    if not session.get('user_email'):
        flash('Please login to view your analysis')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session.get('user_email')).first()
    if not user:
        flash('User not found')
        return redirect(url_for('home'))

    attempts = Score.query.filter_by(user_id=user.id).order_by(Score.time).all()
    if not attempts:
        flash('No attempts yet')
        return render_template('analysis_user.html', chart_data=None, attempts=[])

    # Line plot of scores over time (all attempts)
    times = [a.time for a in attempts]
    scores = [a.score for a in attempts]

    fig = plt.figure(figsize=(6, 4))
    plt.plot_date(times, scores, '-o', color='green')
    plt.xlabel('Time')
    plt.ylabel('Score')
    plt.title(f'Performance Over Time for {user.name}')
    plt.gcf().autofmt_xdate()

    chart_data = 'data:image/png;base64,' + _generate_image_bytes_from_figure(fig)

    # Include attempts table rows
    attempt_rows = []
    for a in attempts:
        quiz = Quiz.query.filter_by(id=a.quiz_id).first()
        attempt_rows.append({'quiz': quiz.name if quiz else 'Unknown', 'score': a.score, 'time': a.time})

    return render_template('analysis_user.html', chart_data=chart_data, attempts=attempt_rows)


@app.route('/my_analysis/<int:quiz_id>')
def my_analysis_quiz(quiz_id):
    if not session.get('user_email'):
        flash('Please login to view your analysis')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session.get('user_email')).first()
    if not user:
        flash('User not found')
        return redirect(url_for('home'))

    attempts = Score.query.filter_by(user_id=user.id, quiz_id=quiz_id).order_by(Score.time).all()
    if not attempts:
        flash('No attempts for this quiz yet')
        return render_template('analysis_user.html', chart_data=None, attempts=[])

    times = [a.time for a in attempts]
    scores = [a.score for a in attempts]

    fig = plt.figure(figsize=(6, 4))
    plt.plot_date(times, scores, '-o', color='orange')
    plt.xlabel('Time')
    plt.ylabel('Score')
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    title_quiz = quiz.name if quiz else f'Quiz {quiz_id}'
    plt.title(f'Performance Over Time for {title_quiz}')
    plt.gcf().autofmt_xdate()

    chart_data = 'data:image/png;base64,' + _generate_image_bytes_from_figure(fig)

    attempt_rows = []
    for a in attempts:
        attempt_rows.append({'quiz': title_quiz, 'score': a.score, 'time': a.time})

    return render_template('analysis_user.html', chart_data=chart_data, attempts=attempt_rows)

# ---------------------------------------------------------------------------