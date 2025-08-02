import os
import re
import time
import psycopg2.extras
from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from utils import *
from flask import current_app
from werkzeug.utils import secure_filename

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses')
def courses():
    if 'username' not in session:
        flash('You must be logged in to view courses.', 'danger')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    role = session.get('role')

    if role == 'admin':
        cur.execute('SELECT id, name, description, badge_image_path FROM courses ORDER BY name')
        all_courses = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('course/courses.html', all_courses=all_courses, is_admin=True)
    cur.execute('SELECT id, can_create_course FROM users WHERE username = %s', (session['username'],))
    user_row = cur.fetchone()

    if not user_row:
        flash('User not found.', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('auth.login'))
    user_id = user_row[0]
    can_create_course = False

    if role == 'teacher':
        can_create_course = user_row[1]
    cur.execute("SELECT course_id FROM completed_courses WHERE user_id = %s", (user_id,))
    completed_ids_result = cur.fetchall()
    completed_course_ids = [row[0] for row in completed_ids_result]
    completed_course_ids_tuple = tuple(completed_course_ids) if completed_course_ids else (None,)
    completed_course_ids_tuple = tuple(completed_course_ids) if completed_course_ids else (0,)
    completed_courses = []

    if completed_course_ids:
        cur.execute("SELECT id, name, description, badge_image_path FROM courses WHERE id IN %s", (tuple(completed_course_ids),))
        completed_courses = cur.fetchall()
    cur.execute(""" SELECT c.id, c.name, c.description, c.badge_image_path FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.user_id = %s AND c.id NOT IN %s """, (user_id, completed_course_ids_tuple))
    enrolled_courses = cur.fetchall()
    cur.execute(""" SELECT id, name, description, badge_image_path FROM courses WHERE id NOT IN (SELECT course_id FROM enrollments WHERE user_id = %s) AND id NOT IN %s """, (user_id, completed_course_ids_tuple))
    available_courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('course/courses.html', enrolled_courses=enrolled_courses, available_courses=available_courses, completed_courses=completed_courses, is_admin=False, can_create_course=can_create_course)

@courses_bp.route('/create_course', methods=['POST'])
def create_course():
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('course.courses'))
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    chapters = []
    chapter_form_indices = set()

    for key in request.form:
        match = re.match(r'chapters\[(\d+)\]\[.+\]', key)
        if match:
            chapter_form_indices.add(int(match.group(1)))

    for form_idx in sorted(list(chapter_form_indices)):
        chapter_title = request.form.get(f'chapters[{form_idx}][title]')

        if chapter_title is None:
            continue
        chapter = {
            'title': chapter_title.strip(),
            'content': request.form.get(f'chapters[{form_idx}][content]', '').strip(),
            'subchapters': [s.strip() for s in request.form.getlist(f'chapters[{form_idx}][subchapters][]') if s.strip()],
            'subchapter_contents': [sc.strip() for sc in request.form.getlist(f'chapters[{form_idx}][subchapter_contents][]') if sc.strip()],
            'exam_type': request.form.get(f'chapters[{form_idx}][exam_type]', ''),
            'quiz_questions': [],
            'written_prompt': request.form.get(f'chapters[{form_idx}][written_prompt]', '').strip(),
            'file_prompt': request.form.get(f'chapters[{form_idx}][file_prompt]', '').strip(),
        }
        quiz_questions_data = []
        q_form_idx = 0

        while True:
            q_text_key = f'chapters[{form_idx}][quiz_questions][{q_form_idx}][question]'
            q_ans_key = f'chapters[{form_idx}][quiz_questions][{q_form_idx}][answer]'
            q_text = request.form.get(q_text_key)

            if q_text is None:
                break
            q_ans = request.form.get(q_ans_key)
            quiz_questions_data.append({'question': q_text.strip(), 'answer': (q_ans.strip() if q_ans else '')})
            q_form_idx += 1
        chapter['quiz_questions'] = quiz_questions_data
        chapters.append(chapter)
    badge_image_file = request.files.get('badge_image')
    badge_path_for_db = None

    if badge_image_file and badge_image_file.filename:
        filename = secure_filename(badge_image_file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        save_path = os.path.join(current_app.config['BADGE_UPLOADS_FOLDER'], unique_filename)
        badge_image_file.save(save_path)
        badge_path_for_db = os.path.join('course_badges', unique_filename).replace("\\", "/")
    conn = get_db_connection()
    cur = conn.cursor()
    teacher_id = get_user_id(session['username'])
    try:
        cur.execute('INSERT INTO courses (name, description, structure, created_by, badge_image_path) VALUES (%s, %s, %s, %s, %s)', (name, description, json.dumps(chapters), teacher_id, badge_path_for_db))
        cur.execute('UPDATE users SET can_create_course = FALSE WHERE username = %s', (session['username'],))
        conn.commit()
        flash('Course created successfully!', 'success')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error creating course: {e}")
        flash('An error occurred while creating the course.', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('courses.courses'))

@courses_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM courses WHERE id = %s', (course_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Course deleted.', 'success')
    return redirect(url_for('courses.courses'))

@courses_bp.route('/course/<int:course_id>/complete', methods=['POST'])
def complete_course(course_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user_id = get_user_id(session['username'])

    if not check_if_course_can_be_completed(user_id, course_id):
        flash("You have not met all the requirements to complete this course yet.", 'danger')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("INSERT INTO completed_courses (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
        cur.execute("SELECT badge_image_path, name FROM courses WHERE id = %s", (course_id,))
        course = cur.fetchone()
        conn.commit()
        flash(f"Congratulations! You have completed the course '{course['name']}' and earned 50 XP!", 'success')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error completing course {course_id} for user {user_id}: {e}")
        flash("An error occurred while completing the course.", 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('courses.courses'))

@courses_bp.route('/propose_course', methods=['POST'])
def propose_course():
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Only teachers can propose courses.', 'danger')
        return redirect(url_for('courses.courses'))
    name = request.form['name']
    description = request.form['description']
    requested_by = session['username']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO pending_courses (name, description, requested_by) VALUES (%s, %s, %s)', (name, description, requested_by))
    conn.commit()
    cur.close()
    conn.close()
    flash('Course proposal submitted for admin approval.', 'success')
    return redirect(url_for('courses.courses'))

@courses_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'username' not in session:
        flash('Please log in to view the course.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT structure FROM courses WHERE id = %s', (course_id,))
    course = cur.fetchone()
    cur.close()
    conn.close()

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses.courses'))
    structure = course[0]

    if isinstance(structure, str):
        structure = json.loads(structure)

    if not structure:
        flash('No chapters found for this course.', 'danger')
        return redirect(url_for('courses.courses'))
    return redirect(url_for('chapters.course_chapter', course_id=course_id, chapter_idx=0))