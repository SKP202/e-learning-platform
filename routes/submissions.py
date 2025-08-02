import os
import psycopg2.extras

from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from flask import send_file
from utils import *
from flask import current_app

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/teacher/submissions')
def teacher_submissions():
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    teacher_id = get_user_id(session['username'])
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(''' SELECT s.id, u.username, c.name AS course_name, s.chapter_idx, s.submission_type, s.submission_data, s.status, s.submission_content, s.teacher_note FROM exam_submissions s JOIN users u ON s.user_id = u.id JOIN courses c ON s.course_id = c.id WHERE c.created_by = %s ORDER BY s.status DESC, s.id DESC ''', (teacher_id,))
    submissions = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('submissions/submissions.html', submissions=submissions)

@submissions_bp.route('/teacher/submissions/<int:submission_id>/approve', methods=['POST'])
def approve_submission(submission_id):
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE exam_submissions SET status = %s WHERE id = %s', ('approved', submission_id))
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    dict_cur.execute(""" SELECT es.user_id, es.teacher_note, es.course_id, es.chapter_idx, c.name AS course_name FROM exam_submissions es JOIN courses c ON es.course_id = c.id WHERE es.id = %s """, (submission_id,))
    submission_details = dict_cur.fetchone()

    if submission_details:
        student_id = submission_details['user_id']
        course_name = submission_details['course_name']
        chapter_idx_for_display = submission_details['chapter_idx'] + 1
        teacher_note = submission_details['teacher_note']
        link = url_for('chapters.course_chapter', course_id=submission_details['course_id'], chapter_idx=submission_details['chapter_idx'], _external=True)
        status_message_part = "approved" if request.endpoint == 'submissions.approve_submission' else "rejected"
        message = f"Your submission for Chapter {chapter_idx_for_display} in course '{course_name}' has been {status_message_part}."

        if teacher_note:
            message += f" Teacher's note: \"{teacher_note}\""
        create_notification(student_id, message)
    dict_cur.close()
    conn.commit()
    cur.close()
    conn.close()
    flash('Submission approved.', 'success')
    return redirect(url_for('submissions.teacher_submissions'))

@submissions_bp.route('/teacher/submissions/<int:submission_id>/reject', methods=['POST'])
def reject_submission(submission_id):
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE exam_submissions SET status = %s WHERE id = %s', ('rejected', submission_id))
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    dict_cur.execute(""" SELECT es.user_id, es.teacher_note, es.course_id, es.chapter_idx, c.name AS course_name FROM exam_submissions es JOIN courses c ON es.course_id = c.id WHERE es.id = %s """, (submission_id,))
    submission_details = dict_cur.fetchone()

    if submission_details:
        student_id = submission_details['user_id']
        course_name = submission_details['course_name']
        chapter_idx_for_display = submission_details['chapter_idx'] + 1
        teacher_note = submission_details['teacher_note']
        link = url_for('chapters.course_chapter', course_id=submission_details['course_id'], chapter_idx=submission_details['chapter_idx'], _external=True)
        status_message_part = "approved" if request.endpoint == 'submissions.approve_submission' else "rejected"
        message = f"Your submission for Chapter {chapter_idx_for_display} in course '{course_name}' has been {status_message_part}."

        if teacher_note:
            message += f" Teacher's note: \"{teacher_note}\""
        create_notification(student_id, message)
    dict_cur.close()
    conn.commit()
    cur.close()
    conn.close()
    flash('Submission rejected.', 'info')
    return redirect(url_for('submissions.teacher_submissions'))

@submissions_bp.route('/teacher/submissions/<int:submission_id>/delete', methods=['POST'])
def delete_submission(submission_id):
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM exam_submissions WHERE id=%s", (submission_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Submission deleted.', 'success')
    return redirect(url_for('submissions.teacher_submissions'))

@submissions_bp.route('/download_submission/<int:submission_id>')
def download_submission(submission_id):
    if 'username' not in session:
        flash('Please log in to download submissions.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT file_path, filename FROM exam_submissions WHERE id = %s AND submission_type = %s', (submission_id, 'file'))
    submission_record = cur.fetchone()
    cur.close()
    conn.close()

    if not submission_record or not submission_record['file_path']:
        flash('File submission record not found or path is missing.', 'danger')
        return redirect(url_for('submissions.teacher_submissions'))
    file_path_on_server = submission_record['file_path']
    original_filename_for_download = submission_record['filename']

    if not os.path.exists(file_path_on_server):
        current_app.logger.error(f"File not found on server at path: {file_path_on_server}")
        flash('Error: The file could not be found on the server. It may have been moved or deleted.', 'danger')
        return redirect(url_for('submissions.teacher_submissions'))
    try:
        return send_file(file_path_on_server, as_attachment=True, download_name=original_filename_for_download)
    except Exception as e:
        current_app.logger.error(f"Error sending file (ID: {submission_id}): {e}")
        flash('An error occurred while trying to send the file.', 'danger')
        return redirect(url_for('submissions.teacher_submissions'))

@submissions_bp.route('/teacher/submission/<int:submission_id>/save_note', methods=['POST'])
def save_teacher_note(submission_id):
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Access denied. Only teachers can add notes.', 'danger')
        return redirect(url_for('auth.login'))
    teacher_id = get_user_id(session['username'])
    note_content = request.form.get('teacher_note', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT 1 FROM exam_submissions es JOIN courses c ON es.course_id = c.id WHERE es.id = %s AND c.created_by = %s """, (submission_id, teacher_id))

        if not cur.fetchone():
            flash('Unauthorized to save note for this submission.', 'danger')
            return redirect(url_for('submissions.teacher_submissions'))
        cur.execute("UPDATE exam_submissions SET teacher_note = %s WHERE id = %s", (note_content, submission_id))
        conn.commit()
        flash('Note saved successfully.', 'success')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error saving teacher note for submission {submission_id}: {e}")
        flash('Failed to save note.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('submissions.teacher_submissions'))