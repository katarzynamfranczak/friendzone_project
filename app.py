from flask import Flask, render_template, url_for, request, redirect, session
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24)


def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_get = db.execute('SELECT * FROM users WHERE user_name = _', [user])
        user = user_get.fetchone()
    return user


# @app.teardown_appcontext  # DATABASE TEAM: here I named the database 'databasename' you can change it for something better
# def close_database(error):
#     if hasattr(g, 'databasename_db'):
#         g.databasename_db.close()


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
        user_get = cursor.execute(f"SELECT * FROM users WHERE user_name = '{user_name}';")
        user = None
        if user_get:
            user = user_get.fetchone()
        else:
            print("USER IS NONE")
        if user:
            if check_password_hash(user, user_created_password):
                print("SUCCESSFUL LOGIN")
                session['user'] = user['user_name']
                return redirect(url_for('home'))
            else:
                print("INCORRECT PASSWORD")
                error = 'Incorrect password'
                # return redirect(url_for('login', loginerror=error)) # might add it back
        # return redirect(url_for('home')) # might add it back
        cursor.close()
    return render_template("login.html", loginerror=error, user=user)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    user = get_current_user()
    signup_error = None

    if request.method == "POST":
        # get info from html form
        user_name = request.form['user_name']
        user_password = request.form['user_password']

        # hash password
        # hashed_password = generate_password_hash(password)

        # connect to database
        db = get_database()  # DATABASE TEAM:  database needs to be done properly
        cursor = db.cursor(buffered=True, dictionary=True)
        # duplicate
        user_get = cursor.execute(f"SELECT * FROM users WHERE user_name = '{user_name}';")
        existing_user = None
        if user_get:
            existing_user = user_get.fetchone()
        print(f"existing user: {existing_user}")
        if existing_user:
            signup_error = 'Username already exists, please set-up different user name'

            return render_template('signup.html', signup_error=signup_error)

        # DATABASE TEAM: sql query to insert this to database table
        cursor.execute(
            f"insert into users (user_name, user_password, email, user_type, user_dob) values ('{user_name}', '{user_password}', 'kf@kf.com', 'user', '1996-01-01');")
        # DATABASE TEAM: make the changes in the database table
        db.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template("signup.html", user=user)


@app.route('/promote')  # methods = ['POST', 'GET']) I might add it back
# DATABASE TEAM: fyi
def promote():
    user = get_current_user()
    db = get_database()
    all_users_get = db.execute('SELECT * FROM users')
    all_databasename = all_users_get.fetchall()
    return render_template('promote.html', user=user)

    # if request.method == 'GET': left it here in case if I will need it
    #     all_users_get = db.execute('SELECT * FROM users')
    #     all_databasename = all_users_get.fetchall()
    #     return redirect(url_for('promote', all_databasename = all_databasename))
    # return render_template('promote.html', user = user)


@app.route(
    '/promote_to_admin/<int:user_id>')  # UPDATING USER, it should create promote and delete options on promote page
def promote_to_admin(user_id):
    user = get_current_user()
    db = get_database()  # DATABASE TEAM: here it will eb updating it in the database
    db.execute('UPDATE Users SET user_type = "admin" WHERE user_id = _',
               [user_id])  # update users table and set admin column as 1 where id is the userid
    db.commit()
    return redirect(url_for('promote'))
    # return render_template('promote.html', user=user)
    # DATABASE TEAM: TESTING/DEBUGGING: it would be useful to change all users to 0 and then promote one to admin to check if it's working


@app.route('/delete_user/<int:user_id>')  # DATABASE TEAM: deleting user
def delete_user(user_id):
    db = get_database()
    db.execute('DELETE FROM Users WHERE user_id = _', [user_id])  # delete users from the table where is = user id
    db.commit()
    return redirect(url_for('promote'))
    # by deleting a user the page will refresh the page itself
    # DATABASE TEAM: it would be useful to delete some user and add see if it's working


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

    # return render_template("logout.html")


if __name__ == "__main__":
    app.run(debug=True)
