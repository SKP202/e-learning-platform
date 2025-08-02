import json
import os
from flask import Flask, session
from routes.admin import admin_bp
from routes.authentication import auth_bp
from routes.chapters import chapters_bp
from routes.courses import courses_bp
from routes.leaderboard import leaderboard_bp
from routes.chat import chat_bp
from routes.notifications import notifications_bp
from routes.report import report_bp
from routes.submissions import submissions_bp
from routes.profile import profile_bp
from routes.welcome import welcome_bp
from routes.enrollment import enrollment_bp
from utils import *
from flask_socketio import  SocketIO
from flask_socketio import emit, join_room, leave_room

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)
UPLOAD_FOLDER = os.path.join('static', 'profile')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BADGE_UPLOADS_FOLDER = os.path.join('static', 'course_badges')
app.config['BADGE_UPLOADS_FOLDER'] = BADGE_UPLOADS_FOLDER

EXAM_UPLOADS_FOLDER = os.path.join('static', 'exam_uploads')
os.makedirs(EXAM_UPLOADS_FOLDER, exist_ok=True)
app.config['EXAM_UPLOADS_FOLDER'] = EXAM_UPLOADS_FOLDER

app.register_blueprint(auth_bp)
app.register_blueprint(submissions_bp)
app.register_blueprint(report_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(chapters_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(welcome_bp)
app.register_blueprint(enrollment_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(leaderboard_bp)


@app.template_filter('loads')
def json_loads_filter(s):
    return json.loads(s)

@app.context_processor
def inject_unread_notification_count():
    unread_count = 0
    if 'username' in session:
        user_id = get_user_id(session['username'])
        if user_id:
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND NOT is_read", (user_id,))
                result = cur.fetchone()
                if result:
                    unread_count = result[0]
            except Exception as e:
                current_app.logger.error(f"Error fetching unread notification count for user {user_id}: {e}")
            finally:
                cur.close()
                conn.close()
    return dict(unread_notification_count=unread_count)

@socketio.on('join_room')
def handle_join_room_event(data):

    if 'username' not in session:
        return
    course_id = data['course_id']
    room = f"course-{course_id}"
    join_room(room)
    emit('status', {'msg': f"{session.get('username')} has entered the chat."}, to=room)

@socketio.on('leave_room')
def handle_leave_room_event(data):

    if 'username' not in session:
        return
    course_id = data['course_id']
    room = f"course-{course_id}"
    leave_room(room)
    emit('status', {'msg': f"{session.get('username')} has left the chat."}, to=room)


@socketio.on('new_message')
def handle_new_message_event(data):

    if 'username' not in session:
        return
    message_text = data['message']
    course_id = data['course_id']
    user_id = get_user_id(session['username'])
    room = f"course-{course_id}"

    if not all([message_text, user_id, course_id]):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(" INSERT INTO chat_messages (course_id, user_id, message_text) VALUES (%s, %s, %s) RETURNING sent_at ", (course_id, user_id, message_text))
    sent_at = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    emit('chat_message', {'username': session.get('username'),'message': message_text,'timestamp': sent_at.strftime('%I:%M %p')}, to=room, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
