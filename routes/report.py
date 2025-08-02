from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from utils import *
from flask import current_app
report_bp = Blueprint('report', __name__)

@report_bp.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    if 'username' not in session or session.get('role') != 'teacher':
        flash('Only teachers can report issues.', 'danger')
        return redirect(url_for('login'))
    teacher_id = get_user_id(session['username'])

    if request.method == 'POST':
        title = request.form.get('issue_title', '').strip()
        description = request.form.get('issue_description', '').strip()

        if not description:
            flash('Issue description cannot be empty.', 'danger')
            return render_template('reports/report_issue.html', title_value=title)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO issue_reports (teacher_id, title, description, status) VALUES (%s, %s, %s, %s)", (teacher_id, title if title else None, description, 'open'))
            conn.commit()
            flash('Issue reported successfully. Admins will review it shortly.', 'success')
            return redirect(url_for('courses.courses'))
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error reporting issue for teacher ID {teacher_id}: {e}")
            flash('Failed to report issue due to a server error. Please try again.', 'danger')
        finally:
            cur.close()
            conn.close()
        return render_template('reports/report_issue.html', title_value=title)

    return render_template('reports/report_issue.html')