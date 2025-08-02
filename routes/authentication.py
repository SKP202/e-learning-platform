import re

from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password, role, verified FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and user[0] == password:
            if user[1] == 'teacher' and not user[2]:
                flash('Your account is pending verification by an admin.', 'danger')
                return render_template('authentication/login.html')
            session['username'] = username
            session['role'] = user[1]
            return redirect(url_for('profile.Profile'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('authentication/login.html')
    return render_template('authentication/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        proof_file = request.files.get('proof')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1 FROM users WHERE username = %s', (username,))

        if cur.fetchone():
            flash('Username already exists.', 'danger')
            cur.close()
            conn.close()
            return render_template('authentication/register.html')


        cur.execute('SELECT 1 FROM users WHERE email = %s', (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            cur.close()
            conn.close()
            return render_template('authentication/register.html')

        if not EMAIL_REGEX.match(email):
            flash('Invalid email address.', 'danger')
            cur.close()
            conn.close()
            return render_template('authentication/register.html')

        if not PASSWORD_REGEX.match(password):
            flash('Password must be at least 8 characters long, contain an uppercase letter, a number, and a symbol.', 'danger')
            cur.close()
            conn.close()
            return render_template('authentication/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            cur.close()
            conn.close()
            return render_template('authentication/register.html')
        proof_data = None

        if role == 'teacher':
            if not proof_file or proof_file.filename == '':
                flash('Teachers must upload proof.', 'danger')
                cur.close()
                conn.close()
                return render_template('authentication/register.html')
            proof_data = proof_file.read()
        verified = True if role == 'student' else False
        cur.execute('INSERT INTO users (username, email, password, role, proof_data, verified) VALUES (%s, %s, %s, %s, %s, %s)', (username, email, password, role, proof_data, verified))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('authentication/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome.welcome'))