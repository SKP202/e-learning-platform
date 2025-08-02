import psycopg2.extras
from flask import Blueprint, render_template, redirect, flash
from flask import session, url_for

from utils import *

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def leaderboard():

    if 'username' not in session:
        flash("You must be logged in to view the leaderboard.", "danger")
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT u.id, u.username, u.profile_pic, COUNT(cc.course_id) AS completed_courses FROM users u LEFT JOIN completed_courses cc ON u.id = cc.user_id GROUP BY u.id, u.username, u.profile_pic ORDER BY completed_courses DESC, u.username ASC LIMIT 50;""")
    top_users_raw = cur.fetchall()
    cur.close()
    conn.close()
    leaderboard_data = []

    for rank, user in enumerate(top_users_raw, 1):
        total_xp = int(user['completed_courses']) * 50
        level = 0
        xp_to_level_up = 50
        courses_needed_per_step = 1
        temp_xp = total_xp

        while temp_xp >= xp_to_level_up:
            temp_xp -= xp_to_level_up
            level += 1
            if level > 0 and level % 2 == 0:
                courses_needed_per_step += 1
            xp_to_level_up = courses_needed_per_step * 50

        leaderboard_data.append({
            'rank': rank,
            'username': user['username'],
            'profile_pic': url_for('static', filename=f"profile/{user['profile_pic']}") if user['profile_pic'] else url_for('static', filename='default_profile.png'),
            'level': level,
            'completed_courses': user['completed_courses'],
            'total_xp': total_xp
        })
    return render_template('leaderboard/leaderboard.html', leaderboard_data=leaderboard_data)