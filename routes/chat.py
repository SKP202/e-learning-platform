import psycopg2.extras
from flask import Blueprint, render_template, redirect, flash
from flask import session, url_for

from utils import *

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/course/<int:course_id>/chat')
def course_chat(course_id):

    if 'username' not in session:
        flash("Please log in to access the course chat.", "danger")
        return redirect(url_for('login'))
    user_id = get_user_id(session['username'])
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT name FROM courses WHERE id = %s", (course_id,))
    course = cur.fetchone()
    cur.execute(""" SELECT cm.message_text, cm.sent_at, u.username FROM chat_messages cm JOIN users u ON cm.user_id = u.id WHERE cm.course_id = %s ORDER BY cm.sent_at ASC """, (course_id,))
    messages = cur.fetchall()
    cur.close()
    conn.close()

    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for('courses'))
    return render_template('chat/course_chat.html', course=course, messages=messages, course_id=course_id)