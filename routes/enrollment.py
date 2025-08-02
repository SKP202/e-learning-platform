from flask import Blueprint, redirect, flash
from flask import session, url_for

from db import get_db_connection

enrollment_bp = Blueprint('enroll', __name__)

@enrollment_bp.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'username' not in session or session.get('role') not in ['student', 'teacher']:
        flash('You must be logged in as a student or teacher to enroll.', 'danger')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s', (session['username'],))
    user_id = cur.fetchone()[0]
    cur.execute('SELECT 1 FROM enrollments WHERE user_id = %s AND course_id = %s', (user_id, course_id))

    if cur.fetchone():
        flash('You are already enrolled in this course.', 'info')
    else:
        cur.execute('INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)', (user_id, course_id))
        conn.commit()
        flash('Enrolled successfully!', 'success')

    cur.close()
    conn.close()
    return redirect(url_for('courses.courses'))

@enrollment_bp.route('/unenroll/<int:course_id>')
def unenroll(course_id):
    if 'username' not in session or session.get('role') not in ['student', 'teacher']:
        flash('You must be logged in as a student or teacher to unenroll.', 'danger')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s', (session['username'],))
    user_id = cur.fetchone()[0]
    cur.execute('DELETE FROM enrollments WHERE user_id = %s AND course_id = %s', (user_id, course_id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Unenrolled successfully!', 'success')
    return redirect(url_for('courses.courses'))