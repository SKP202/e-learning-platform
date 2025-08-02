import psycopg2.extras
import io
from flask import Blueprint, render_template, request, redirect, flash
from flask import session, url_for
from flask import send_file
from utils import *
from flask import current_app
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT id, username, email, proof_path FROM users WHERE role = %s AND verified = FALSE', ('teacher',))
    teacher_requests = cur.fetchall()
    cur.execute('SELECT id, name, description, requested_by FROM pending_courses')
    course_requests = cur.fetchall()
    cur.execute(''' SELECT ir.id, ir.title, ir.description, ir.status, ir.reported_at, u.username AS teacher_username FROM issue_reports ir JOIN users u ON ir.teacher_id = u.id ORDER BY ir.status ASC, ir.reported_at DESC ''')
    issue_reports = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/admin.html', teacher_requests=teacher_requests, course_requests=course_requests, issue_reports=issue_reports)

@admin_bp.route('/admin/proof/<int:user_id>')
def get_proof(user_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT proof_data FROM users WHERE id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row[0]:
        return send_file(io.BytesIO(row[0]), mimetype='image/jpeg', as_attachment=True, download_name='proof.jpg')
    else:
        flash('No proof found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/verify_teacher/<int:user_id>')
def verify_teacher(user_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET verified = TRUE WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Teacher verified.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/reject_teacher/<int:user_id>')
def reject_teacher(user_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Teacher request rejected.', 'info')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/approve_course/<int:proposal_id>')
def approve_course(proposal_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute('SELECT id, name, description, requested_by FROM pending_courses WHERE id = %s', (proposal_id,))
        proposal = cur.fetchone()

        if proposal:
            teacher_username = proposal['requested_by']
            cur.execute('UPDATE users SET can_create_course = TRUE WHERE username = %s', (teacher_username,))
            cur.execute('DELETE FROM pending_courses WHERE id = %s', (proposal_id,))
            conn.commit()
            flash(f"Course proposal '{proposal['name']}' approved. Teacher {teacher_username} can now create the course.",'success')
            teacher_user_id = get_user_id(teacher_username)

            if teacher_user_id:
                courses_page_link = url_for('courses.courses', _external=True)
                notification_message = f"Your course proposal '{proposal['name']}' has been approved! You can now create this course from the 'Courses' page."
                create_notification(teacher_user_id, notification_message)
            else:
                current_app.logger.warning(
                    f"Could not find user ID for teacher '{teacher_username}' to send approval notification.")
        else:
            flash('Course proposal not found.', 'danger')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error approving course proposal ID {proposal_id}: {e}")
        flash('An error occurred while approving the course proposal.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/reject_course/<int:proposal_id>')
def reject_course(proposal_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    proposal_name_for_notification = f"ID {proposal_id}"
    teacher_username_for_notification = None
    try:
        cur.execute('SELECT name, requested_by FROM pending_courses WHERE id = %s', (proposal_id,))
        proposal_details = cur.fetchone()

        if proposal_details:
            proposal_name_for_notification = proposal_details['name']
            teacher_username_for_notification = proposal_details['requested_by']
        else:
            current_app.logger.warning(
                f"Admin attempted to reject course proposal ID {proposal_id}, but it was not found before deletion.")
        cur.execute('DELETE FROM pending_courses WHERE id = %s RETURNING id', (proposal_id,))
        deleted_row = cur.fetchone()
        if deleted_row:
            conn.commit()
            flash('Course proposal rejected successfully.', 'info')
            if teacher_username_for_notification:
                teacher_user_id = get_user_id(teacher_username_for_notification)
                if teacher_user_id:
                    courses_page_link = url_for('courses.courses', _external=True)
                    notification_message = f"Unfortunately, your course proposal '{proposal_name_for_notification}' was not approved at this time."
                    create_notification(teacher_user_id, notification_message)
                else:
                    current_app.logger.warning(
                        f"Could not find user ID for teacher '{teacher_username_for_notification}' to send rejection notification for proposal '{proposal_name_for_notification}'.")
        else:
            conn.rollback()
            flash(f'Course proposal with ID {proposal_id} not found or already deleted.', 'warning')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error rejecting course proposal ID {proposal_id}: {e}")
        flash('An error occurred while rejecting the course proposal.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/issue/<int:report_id>/update_status', methods=['POST'])
def update_issue_status(report_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    new_status = request.form.get('new_status')
    valid_statuses = ['open', 'in_progress', 'resolved', 'closed']

    if not new_status or new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE issue_reports SET status = %s WHERE id = %s", (new_status, report_id))
        conn.commit()
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        dict_cur.execute("SELECT teacher_id, title FROM issue_reports WHERE id = %s", (report_id,))
        report_info = dict_cur.fetchone()
        dict_cur.close()

        if report_info and report_info['teacher_id']:
            teacher_id_reporter = report_info['teacher_id']
            issue_title_str = f"'{report_info['title']}'" if report_info['title'] else f"ID {report_id}"
            message = f"An admin updated the status of your issue report {issue_title_str} to '{new_status}'."
            create_notification(teacher_id_reporter, message)
        flash(f'Issue report ID {report_id} status updated to {new_status}.', 'success')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating status for issue report {report_id}: {e}")
        flash('Failed to update issue status.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/issue/<int:report_id>/delete', methods=['POST'])
def delete_issue_report(report_id):

    if 'username' not in session or session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM issue_reports WHERE id = %s", (report_id,))
        conn.commit()
        flash(f'Issue report ID {report_id} deleted.', 'success')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error deleting issue report {report_id}: {e}")
        flash('Failed to delete issue report.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.admin_dashboard'))