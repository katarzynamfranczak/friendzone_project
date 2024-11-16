from datetime import datetime

from friendzone_project.app.extensions import _get_database


class DbConnectionError(Exception):
    pass


def encryption_message(message=""):
    # Encryption of the message: 'Caesar Cipher'

    alphabet = ".,'() abcdefghijklmnopqrstuvwxyz!/#?[];:\"'ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 2
    key = 3
    get_letter, keyword = 0, []

    if message not in ("", None):
        for letter in message:
            if letter in alphabet:
                get_letter = alphabet.index(letter) + key
                keyword.append(alphabet[get_letter])
            else:
                keyword.append(letter)

        return "".join(keyword)

    return None


def decryption_message(message=""):
    # Decryption of the message: 'Caesar Cipher'

    alphabet = ".,'() abcdefghijklmnopqrstuvwxyz!/#?[];:\"'ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 2
    key = 3
    get_letter, keyword = 0, []

    if message not in ("", None):
        for letter in message:
            if letter in alphabet:
                get_letter = alphabet.index(letter) - key
                keyword.append(alphabet[get_letter])
            else:
                keyword.append(letter)

        return "".join(keyword)

    return None


def show_all_messages(receiver_id):
    query = """
    SELECT sender_id, date_time, message, isRead 
    FROM Messages 
    WHERE receiver_id = %s
    ORDER BY date_time DESC
    LIMIT 50;
    """
    values = receiver_id

    # Check if user has chat history
    try:
        db = _get_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, values)
        db_info = cursor.fetchall()

        for item in db_info:
            item['message'] = decryption_message(item['message'])

        cursor.close()

    except DbConnectionError as e:
        print(f"Error fetching contact list: {e}. \nUser has no message history")
        db_info = None

    return db_info


def show_message_thread(receiver_id, sender_id):
    # Show history of chat with one particular user
    query = """
    SELECT sender_id, date_time, message, isRead 
    FROM Messages 
    WHERE (receiver_id = %s AND sender_id = %s)  OR (receiver_id = %s AND sender_id = %s)
    ORDER BY date_time DESC
    """
    values = (receiver_id, sender_id, sender_id, receiver_id)

    try:
        db = _get_database()
        cursor = db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, values)
        db_info = cursor.fetchall()

        for item in db_info:
            item['message'] = decryption_message(item['message'])

        cursor.close()

    except DbConnectionError as e:
        print(f"Error fetching contact list: {e}. \nUser has no message history")
        db_info = None

    return db_info


def delete_message_thread(receiver_id, sender_id):
    query = """
    DELETE FROM messages
    WHERE (receiver_id = %s AND sender_id = %s) OR (receiver_id = %s AND sender_id = %s);
    """
    values = (receiver_id, sender_id, sender_id, receiver_id)

    try:
        db = _get_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, values)

        # Check how many rows were affected (deleted)
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            print(f"Successfully deleted {rows_affected} messages.")
        else:
            print("No messages found to delete.")

        # Commit the changes to the database (necessary for DELETE)
        db.commit()

        cursor.close()

        return rows_affected

    except DbConnectionError as e:
        print(f"Error deleting message thread: {e}. \nUser has no message history.")
        return None


def send_message(message, user_id, send_to_id):
    encrypted_msg = encryption_message(message)
    query = """
    INSERT INTO messages (sender_id, receiver_id, date_time, message, isRead) VALUES
    (%s, %s, %s, %s, %s);
    """
    values = (user_id, send_to_id, datetime.now(), encrypted_msg, False)

    try:
        db = _get_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, values)
        db.commit()
        cursor.close()

    except Exception as e:  # Catch any exception (not just DbConnectionError)
        print(f"Error sending message: {e}.")
        db.rollback()  # Rollback in case of error to avoid partial commits

    return show_message_thread(user_id, send_to_id)

