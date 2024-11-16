from flask import render_template, session, redirect, url_for, flash
from mysql.connector import IntegrityError

from . import admin_bp
from friendzone_project.app.extensions import _get_database, _get_current_user


@admin_bp.route('/', methods=['POST', 'GET'])
def promote():
    # Make sure only authorised users can access this page
    if 'user_type' not in session or session.get('user_type') != "admin":
        flash("I'm sorry, you do not have permission to view that page", category='error')
        return redirect(url_for('home.home'))

    user = _get_current_user()
    db = _get_database()

    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()
    cursor.close()

    return render_template('promote.html', user=user, all_users=all_users)


@admin_bp.route('/promote_to_admin/<int:user_id>')
def promote_to_admin(user_id):
    # Make sure only authorised users can access this page
    if 'user_type' not in session or session.get('user_type') != "admin":
        flash("I'm sorry, you do not have permission to view that page", category='error')
        return redirect(url_for('home.home'))

    db = _get_database()

    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("UPDATE users SET user_type = 'admin' WHERE user_id = %s", [user_id])
    db.commit()
    cursor.close()

    flash(f"User with ID {user_id} has been promoted to admin.", category='error')
    return redirect(url_for('admin.promote'))


@admin_bp.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    # Make sure only authorised users can access this page
    if 'user_type' not in session or session.get('user_type') != "admin":
        flash("I'm sorry, you do not have permission to view that page", category='error')
        return redirect(url_for('home.home'))
    try:
        db = _get_database()
        cursor = db.cursor(buffered=True, dictionary=True)
        cursor.execute('DELETE FROM Users WHERE user_id = %s', [user_id])
        db.commit()
        cursor.close()

        flash(f"User with ID {user_id} has been deleted.", category='error')
        return redirect(url_for('admin.promote'))

    except IntegrityError as e:
        if e.errno == 1451:  # Error code for foreign key constraint failure
            flash(f'Cannot delete user {user_id} because of a foreign key constraint.', category='error')

            return redirect(url_for('admin.promote'))



