import psycopg2
import psycopg2.extras
import json
from db import get_db_connection
from flask import current_app

def get_user_id(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s', (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def create_notification(user_id, message, link_url=None):
    if not user_id:
        current_app.logger.warning("Attempted to create notification for invalid user_id.")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO notifications (user_id, message, link_url) VALUES (%s, %s, %s)",
            (user_id, message, link_url)
        )
        conn.commit()
        current_app.logger.info(f"Notification created for user_id {user_id}: {message[:50]}...")
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error creating notification for user {user_id}: {e}")
    finally:
        cur.close()
        conn.close()

def calculate_user_stats(user_id):
    stats = {
        'level': 0, 'total_xp': 0, 'xp_for_next_level': 50,
        'xp_progress': 0, 'completed_courses': 0, 'enrolled_courses': 0,
        'badges': []
    }
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT COUNT(*) AS count FROM completed_courses WHERE user_id = %s", (user_id,))
        stats['completed_courses'] = cur.fetchone()['count']
        cur.execute("""
                    SELECT COUNT(*)
                    FROM enrollments
                    WHERE user_id = %s
                      AND course_id NOT IN (SELECT course_id FROM completed_courses WHERE user_id = %s)
                    """, (user_id, user_id))
        stats['enrolled_courses'] = cur.fetchone()['count']
        stats['total_xp'] = stats['completed_courses'] * 50
        level = 0
        xp_to_level_up = 50
        courses_needed_per_step = 1
        xp_of_current_level = 0

        temp_xp = stats['total_xp']
        while temp_xp >= xp_to_level_up:
            temp_xp -= xp_to_level_up
            level += 1
            if level > 0 and level % 2 == 0:
                courses_needed_per_step += 1
            xp_to_level_up = courses_needed_per_step * 50

        stats['level'] = level
        stats['xp_progress'] = temp_xp
        stats['xp_for_next_level'] = xp_to_level_up
        cur.execute("""
                    SELECT c.name AS course_name, c.badge_image_path
                    FROM completed_courses cc
                             JOIN courses c ON cc.course_id = c.id
                    WHERE cc.user_id = %s
                      AND c.badge_image_path IS NOT NULL
                    """, (user_id,))
        stats['badges'] = cur.fetchall()
    except Exception as e:
        current_app.logger.error(f"Error calculating stats for user {user_id}: {e}")
    finally:
        cur.close()
        conn.close()
    return stats

def check_if_course_can_be_completed(user_id, course_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    can_complete = False
    try:
        cur.execute("SELECT id FROM completed_courses WHERE user_id = %s AND course_id = %s", (user_id, course_id))
        if cur.fetchone():
            return False
        cur.execute("SELECT structure FROM courses WHERE id = %s", (course_id,))
        course_data = cur.fetchone()

        if not (course_data and course_data.get('structure')):
            return False

        chapters_with_exams = []
        structure = course_data['structure']
        if isinstance(structure, str):
            try:
                structure = json.loads(structure)
            except json.JSONDecodeError:
                structure = []

        if isinstance(structure, list):
            for i, chapter in enumerate(structure):
                if chapter.get('exam_type'):
                    chapters_with_exams.append(i)

        if not chapters_with_exams:
            return False
        cur.execute("""
                    SELECT DISTINCT chapter_idx
                    FROM exam_submissions
                    WHERE user_id = %s
                      AND course_id = %s
                      AND status = 'approved'
                    """, (user_id, course_id))
        approved_submissions_results = cur.fetchall()
        chapters_with_approved_submissions = {row['chapter_idx'] for row in approved_submissions_results}
        if set(chapters_with_exams) == chapters_with_approved_submissions:
            can_complete = True

    except Exception as e:
        current_app.logger.error(f"Error in check_if_course_can_be_completed for user {user_id}, course {course_id}: {e}")
        can_complete = False
    finally:
        cur.close()
        conn.close()

    return can_complete

def is_course_completed_by_user(user_id, course_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM completed_courses WHERE user_id = %s AND course_id = %s", (user_id, course_id))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None