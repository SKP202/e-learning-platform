import os
import time
import psycopg2.extras
from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from werkzeug.utils import secure_filename
from utils import *
from flask import current_app
chapters_bp = Blueprint('chapters', __name__)

@chapters_bp.route('/course/<int:course_id>/chapter/<int:chapter_idx>')
def course_chapter(course_id, chapter_idx):
    if 'username' not in session:
        flash('Please log in to view the course.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = get_user_id(session['username'])
    if not user_id:
        return redirect(url_for('auth.login'))

    if is_course_completed_by_user(user_id, course_id):
        flash("You have already completed this course.", 'info')
        return redirect(url_for('courses.courses'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT name, structure FROM courses WHERE id = %s', (course_id,))
    course = cur.fetchone()

    if not course:
        cur.close()
        conn.close()
        flash('Course not found.', 'danger')
        return redirect(url_for('courses.courses'))
    is_ready_to_complete = check_if_course_can_be_completed(user_id, course_id)
    course_name = course['name']
    structure = course['structure']

    if isinstance(structure, str):
        try:
            structure = json.loads(structure)
        except json.JSONDecodeError:
            structure = []

    if not isinstance(structure, list) or not (0 <= chapter_idx < len(structure)):
        cur.close()
        conn.close()
        flash('Chapter not found.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    chapter = structure[chapter_idx]
    total_chapters = len(structure)
    cur.close()
    conn.close()
    return render_template('chapters/chapter_Detail.html', course_id=course_id, course_name=course_name, chapter=chapter, chapter_idx=chapter_idx, total_chapters=total_chapters, zip=zip, can_complete_course=is_ready_to_complete)

@chapters_bp.route('/course/<int:course_id>/chapter/<int:chapter_idx>/exam', methods=['GET', 'POST'])
def chapter_exam(course_id, chapter_idx):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user_id = get_user_id(session['username'])

    if not user_id:
        return redirect(url_for('auth.login'))

    if is_course_completed_by_user(user_id, course_id):
        flash("You have already completed this course and cannot access its exams.", 'info')
        return redirect(url_for('courses.courses'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT structure FROM courses WHERE id = %s", (course_id,))
    course_data = cur.fetchone()

    if not course_data:
        cur.close()
        conn.close()
        flash('Course not found.', 'danger')
        return redirect(url_for('courses.courses'))
    structure = course_data.get('structure', [])

    if isinstance(structure, str):
        try:
            chapters = json.loads(structure)
        except json.JSONDecodeError:
            chapters = []
    else:
        chapters = structure

    if not isinstance(chapters, list) or not (0 <= chapter_idx < len(chapters)):
        cur.close()
        conn.close()
        flash('Chapter not found.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    chapter = chapters[chapter_idx]
    exam_type = chapter.get('exam_type')

    if request.method == 'POST':
        if exam_type == 'quiz':
            answers = []

            for idx, q in enumerate(chapter.get('quiz_questions', [])):
                user_answer = request.form.get(f'answer_{idx}')
                answers.append({'question': q['question'], 'answer': user_answer})
            quiz_answers = json.dumps(answers)
            cur.execute("INSERT INTO exam_submissions (user_id, course_id, chapter_idx, submission_type, submission_data, status) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, course_id, chapter_idx, 'quiz', quiz_answers, 'pending'))

        elif exam_type == 'written':
            written_response = request.form.get('written_response', '').strip()
            cur.execute("INSERT INTO exam_submissions (user_id, course_id, chapter_idx, submission_type, submission_content, status) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, course_id, chapter_idx, 'written', written_response, 'pending'))

        elif exam_type == 'file_upload':
            file = request.files.get('exam_file')

            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"user{user_id}_course{course_id}_chapter{chapter_idx}_{int(time.time())}_{filename}"
                full_save_path = os.path.join(current_app.config['EXAM_UPLOADS_FOLDER'], unique_filename)
                file.save(full_save_path)
                path_for_database = full_save_path.replace("\\", "/")
                cur.execute(
                    "INSERT INTO exam_submissions (user_id, course_id, chapter_idx, submission_type, filename, file_path, status) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_id, course_id, chapter_idx, 'file', filename, path_for_database, 'pending'))
            else:
                flash('No file selected.', 'danger')
                cur.close()
                conn.close()
                return redirect(request.url)
        conn.commit()
        flash(f'{exam_type.replace("_", " ").capitalize()} submitted successfully!', 'success')
        cur.execute("SELECT created_by, name FROM courses WHERE id = %s", (course_id,))
        course_info = cur.fetchone()

        if course_info and course_info['created_by']:
            teacher_id = course_info['created_by']
            course_name = course_info['name']
            student_username = session.get('username', 'A student')
            link = url_for('submissions.teacher_submissions', _external=True)
            message = f"{student_username} submitted work for Chapter {chapter_idx + 1} in your course '{course_name}'."
            create_notification(teacher_id, message, link)
        cur.close()
        conn.close()
        return redirect(url_for('chapters.course_chapter', course_id=course_id, chapter_idx=chapter_idx))
    cur.close()
    conn.close()

    if exam_type:
        template_name = f'exams/exam_{exam_type}.html'
        return render_template(template_name, chapter=chapter, course_id=course_id, chapter_idx=chapter_idx)
    else:
        flash('No exam for this chapter.', 'info')
        return redirect(url_for('chapters.course_chapter', course_id=course_id, chapter_idx=chapter_idx))
