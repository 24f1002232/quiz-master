from controllers.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(100),nullable = False, default = "user")
    scores = db.relationship('Score', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    qualification_req = db.Column(db.String(100), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subj_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chap_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Integer, nullable=False)    
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    opt_a = db.Column(db.String(100), nullable=False)
    opt_b = db.Column(db.String(100), nullable=False)
    opt_c = db.Column(db.String(100), nullable=False)
    opt_d = db.Column(db.String(100), nullable=False)
    ans = db.Column(db.String(1), nullable=False) 

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
