import psycopg2.extras
from flask import Blueprint, render_template, redirect, flash
from flask import session, url_for
from utils import *

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
def view_notifications():
    if 'username' not in session:
        flash('Please log in to view notifications.', 'danger')
        return redirect(url_for('auth.login'))
    user_id = get_user_id(session['username'])

    if not user_id:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, message, is_read, created_at, link_url FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    notifications_list = cur.fetchall()
    unread_ids_to_mark = [n['id'] for n in notifications_list if not n['is_read']]

    if unread_ids_to_mark:
        try:
            placeholders = ', '.join(['%s'] * len(unread_ids_to_mark))
            update_query = f"UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND id IN ({placeholders})"
            update_args = [user_id] + unread_ids_to_mark
            cur.execute(update_query, tuple(update_args))
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error marking notifications as read for user {user_id}: {e}")
    cur.close()
    conn.close()
    return render_template('notifications/notifications.html', notifications=notifications_list)

@notifications_bp.route('/notification/<int:notification_id>/delete', methods=['POST'])
def delete_notification(notification_id):
    if 'username' not in session:
        flash('Please log in to manage notifications.', 'danger')
        return redirect(url_for('auth.login'))
    user_id = get_user_id(session['username'])

    if not user_id:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM notifications WHERE id = %s AND user_id = %s", (notification_id, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error deleting notification {notification_id} for user {user_id}: {e}")
        flash('An error occurred while deleting the notification.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('notifications.view_notifications'))
