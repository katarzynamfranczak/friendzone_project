from flask import request, render_template, session, redirect, url_for, flash

from . import messages_bp
from friendzone_project.app.messages.services import show_message_thread, show_all_messages, delete_message_thread, send_message


# Messages Home
@messages_bp.route("/")
def messages():
    # Make sure only authorised users can access this page
    if 'username' not in session:
        flash('You need to Log In or Sign Up before you can access that feature', category='error')
        return redirect(url_for('home.login'))

    result = show_all_messages([session.get('user_id')])
    session['msg_list'] = result
    return render_template('messages.html', data=result)


#Show chat
@messages_bp.route('/thread', methods=['POST'])
def full_thread():
    # Make sure only authorised users can access this page
    if 'username' not in session:
        flash('You need to Log In or Sign Up before you can access that feature', category='error')
        return redirect(url_for('home.login'))

    sender_id = request.form.get('sender_id')
    session['sender_id'] = sender_id
    result = show_message_thread(session.get('user_id'), sender_id=sender_id)
    return render_template('messages_thread.html', data=result)


@messages_bp.route("/delete", methods=['POST'])
def delete_message():
    # Make sure only authorised users can access this page
    if 'username' not in session:
        flash('You need to Log In or Sign Up before you can access that feature', category='error')
        return redirect(url_for('home.login'))

    sender = session.get('sender_id')

    rows_deleted = delete_message_thread(session.get('user_id'), sender)

    if rows_deleted > 0:
        flash(f'Message thread deleted with user: {sender}')
    else:
        flash(f'No messages found to delete with user: {sender}', category='error')

    return redirect(url_for('messages.messages'))


@messages_bp.route('/reply', methods=['POST'])
def reply():
    # Make sure only authorised users can access this page
    if 'username' not in session:
        flash('You need to Log In or Sign Up before you can access that feature', category='error')
        return redirect(url_for('home.login'))

    # Ensure messages can only be sent on an active thread
    send_to_id = request.form.get('sender_id')
    session['sender_id'] = send_to_id
    message = request.form.get('message')
    result = send_message(message, session.get('user_id'), send_to_id)

    return render_template('messages_thread.html', data=result)
