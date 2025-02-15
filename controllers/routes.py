from app import app
from flask import render_template, request, redirect, session, url_for, flash
from controllers.models import *
import matplotlib.pyplot as plt
import matplotlib


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user1 = User.query.filter_by(email = email).first()
        
        if not user1:
            flash('User not found')
            return redirect(url_for('register'))
        if user1.password != password:
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


@app.route('/register',methods = ['GET','POST'])
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
        
        if User.query.filter_by(email = email).first():
            flash('User already exists')
            return render_template('register.html')

        user = User(
            name = name,
            email = email,
            password = password,
            qualification = qualification,
            role = "user"
            )
        db.session.add(user)
        db.session.commit()

        flash('Registration Successfull!, Login in to continue')
        return redirect(url_for('login'))
    
@app.route('/manage_users')
def manage_users():
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    users = User.query.filter_by(role = "user").all()
    return render_template('manage_users.html',users = users)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if not session.get('user_email') or session.get('role') != 'admin':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    
    user = User.query.filter_by(id = id).first()
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
    