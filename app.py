from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from database import get_database
import os
from datetime import datetime
import sys



app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'
sys.setrecursionlimit(100)


def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        cursor = db.cursor(buffered=True, dictionary=True)
        cursor.execute(f"SELECT * FROM users WHERE user_name = '{user}';")
        user = cursor.fetchone()
        cursor.close()
    return user


@app.route("/home")
@app.route("/")
def home():
    user = get_current_user()

    return render_template("home.html", user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    user = get_current_user()

    error = None

    if request.method == "POST":
        # get info from html form
        user_name = request.form['user_name']
        user_created_password = request.form['user_password']
        db = get_database()
        cursor = db.cursor(buffered=True, dictionary=True)
        print(f"INPUTS: {user_name}, {user_created_password}")
        cursor.execute(f"SELECT * FROM Users WHERE user_name = '{user_name}';")
        user = cursor.fetchone()
        if user:
            if bcrypt.check_password_hash(user['user_password'], user_created_password):
                print("SUCCESSFUL LOGIN")
                session['user'] = user['user_name']
                return render_template("home.html", user_details=user)
            else:
                print("INCORRECT PASSWORD")
                error = 'Incorrect password'

        cursor.close()
    return render_template("login.html", loginerror=error, user=user)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    user = get_current_user()
    signup_error = None

    if request.method == "POST":
        # get info from html form
        user_name = request.form['user_name']
        email = request.form['email']
        user_dob = request.form['user_dob']

        user_dob = datetime.strptime(user_dob, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - user_dob.year - ((today.month, today.day) < (user_dob.month, user_dob.day))

        if age <= 18:
            flash('You must be at least 18 years old to signup to Friendzone')
            #catch try except error 'mysql.connector.errors.DatabaseError: 3819 (HY000): Check constraint 'age_restriction' is violated.'

        # we want to encrypt the password before storing in db
        user_password = bcrypt.generate_password_hash(
            request.form['user_password']
        ).decode('utf-8')

        # connect to database
        db = get_database()
        cursor = db.cursor(buffered=True, dictionary=True)
        # duplicate
        cursor.execute(f"SELECT * FROM users WHERE user_name = '{user_name}';")
        existing_user = cursor.fetchone()
        print(f"existing user: {existing_user}")
        if existing_user:
            signup_error = 'Username already exists, please set-up different user name'

            return render_template('signup.html', signup_error=signup_error)

        cursor.execute(
            f"insert into users (user_name, user_password, email, user_type, user_dob) values ('{user_name}', '{user_password}', '{email}', 'user', '{user_dob}');")

        db.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template("signup.html", user=user)
@app.route('/promote', methods=['POST', 'GET'])
def promote():
    user = get_current_user()
    db = get_database()

    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()
    cursor.close()

    return render_template('promote.html', user=user, all_users=all_users)

@app.route('/promote_to_admin/<int:user_id>')
def promote_to_admin(user_id):
    db = get_database()

    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("UPDATE users SET user_type = 'admin' WHERE user_id = %s", (user_id,))
    db.commit()
    cursor.close()

    flash(f"User with ID {user_id} has been promoted to admin.")

    return redirect(url_for('promote'))





@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    db = get_database()
    db.execute('DELETE FROM Users WHERE user_id = _', [user_id])
    db.commit()
    return redirect(url_for('promote'))



@app.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        email = request.form['email']

        # setting new password
        new_user_password = bcrypt.generate_password_hash(
            request.form['user_password']
        ).decode('utf-8')

        # connect to database | needs more work, it does not change the password
        db = get_database()
        cursor = db.cursor(buffered=True, dictionary=True)

        cursor.execute(
            f"UPDATE users SET user_password = '{new_user_password}' WHERE email = '{email}';")
        db.commit()
        cursor.close()

        return redirect(url_for('login'))


    return render_template("change_password.html")
    # how to direct the user to log in page?


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
