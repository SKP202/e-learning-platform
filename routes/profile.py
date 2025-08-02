import os
import psycopg2.extras
from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from utils import *
from flask import current_app
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
def Profile():
    if 'username' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    username = session['username']
    user_id = get_user_id(username)

    if not user_id:
        flash('User not found. Please log in again.', 'danger')
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('profile_pic')

        if file and file.filename:
            filename = file.filename
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            pic_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(pic_path)
            cur.execute('UPDATE users SET profile_pic = %s WHERE id = %s', (filename, user_id))
            conn.commit()
            flash('Profile picture updated!', 'success')
            return redirect(url_for('profile.Profile'))

    cur.execute('SELECT username, profile_pic, role FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    user_stats = calculate_user_stats(user_id)
    cur.close()
    conn.close()

    if not user:
        flash('Could not retrieve user profile.', 'danger')
        return redirect(url_for('courses.courses'))
    profile_pic_url = url_for('static', filename=f'profile/{user["profile_pic"]}') if user["profile_pic"] else url_for('static', filename='default_profile.png')
    return render_template('profile/profile.html', username=user['username'], profile_pic=profile_pic_url, role=user['role'], stats=user_stats)