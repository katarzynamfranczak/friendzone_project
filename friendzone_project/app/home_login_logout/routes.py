from flask import request, render_template, session, redirect, url_for, flash
import mysql.connector

from . import home_bp
from friendzone_project.app.extensions import bcrypt, _clear_session_except, _get_database, _get_current_user
from friendzone_project.app.home_login_logout.services import LoginValidators, _InvalidPasswordException, _InvalidEmailException, _InvalidAccountException


@home_bp.route("/")
@home_bp.route("/home")
def home():
    # Clear previous search variables
    _clear_session_except(['username', 'user_id', 'user_type', '_flashes'])
    user = _get_current_user() # If logged in, else no user
    return render_template("home.html", user=user)


@home_bp.route("/login", methods=["POST", "GET"])
def login():
    user = _get_current_user()

    if request.method == "POST":
        # get info from html form
        user_name = request.form['user_name']
        user_created_password = request.form['user_password']
        db = _get_database()
        cursor = db.cursor(buffered=True, dictionary=True)

        cursor.execute(f"SELECT * FROM Users WHERE user_name = '{user_name}';")

        user = cursor.fetchone()

        # If user is valid check the inputted password is same as stored hash
        if user:
            if bcrypt.check_password_hash(user['user_password'], user_created_password):
                print("SUCCESSFUL LOGIN")
                session.update({
                    'username' : user_name,
                    'user_type' : user['user_type'],
                    'user_id' : user['user_id']
                })
                return render_template("home_logged_in.html", user_details=user)

            else:
                print("INCORRECT PASSWORD OR USERNAME")
                flash('Incorrect username or password', category='error')
        else:
            print("INCORRECT PASSWORD OR USERNAME")
            flash('Incorrect username or password', category='error')

        cursor.close()

    return render_template("login.html", use =user)


@home_bp.route("/signup", methods=["POST", "GET"])
def signup():
    user = _get_current_user() # Should be none if they are signing up

    if request.method == "POST":
        # get info from html form
        user_name = request.form['user_name']
        email = request.form['email']
        user_dob = request.form['user_dob']
        raw_password = request.form['user_password']

        # we are validating the raw password
        try:
            if not LoginValidators.valid_email(email):
                raise _InvalidEmailException("Invalid email format. Please try again.")

            LoginValidators.reset_password_validation_flags(session)
            LoginValidators.validate_user_password(raw_password)

        except _InvalidPasswordException as e:
            flash(str(e), category='error')
            return render_template('signup.html')

        except _InvalidEmailException as e:
            flash(str(e), category='error')
            return render_template('signup.html')

        # we want to encrypt the password before storing in db
        user_password = bcrypt.generate_password_hash(request.form['user_password']).decode('utf-8')
        _clear_session_except(['_flashes'])

        # user age validation
        try:
            db = _get_database()
            cursor = db.cursor(buffered=True, dictionary=True)
            cursor.execute(f"SELECT * FROM users WHERE user_name = '{user_name}';")
            existing_user = cursor.fetchone()
            print(f"existing user: {existing_user}")

            if existing_user:
                flash('Username already exists, please set-up different user name', category='error')
                return render_template('signup.html')

            cursor.execute(
                f"INSERT INTO users (user_name, user_password, email, user_type, user_dob) values ('{user_name}', '{user_password}', '{email}', 'user', '{user_dob}');")
            db.commit()
            cursor.close()

            return redirect(url_for('home.login'))

        except mysql.connector.errors.DatabaseError as e:
            if e.errno == 3819:
                flash("Stop it, you're a minor! Friendzone is for adults.", category='error')
            return render_template("signup.html", user=user)

    # Set session vars to be checked during password validation - these alter css
    LoginValidators.reset_password_validation_flags(session)

    return render_template('signup.html', user=user)


@home_bp.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        email = request.form['email']

        # Set session vars to be checked during password validation - these alter css
        LoginValidators.reset_password_validation_flags(session)

        try:
            if not LoginValidators.valid_account(email):
                raise _InvalidAccountException('No matching account found.')

            LoginValidators.validate_user_password(request.form['user_password'])
            LoginValidators.reset_password_validation_flags(session)

        except _InvalidAccountException as e:
            flash(str(e), category='error')
            return render_template("change_password.html")

        except _InvalidPasswordException as e:
            flash(str(e), category='error')
            return render_template("change_password.html")

        # setting new password
        new_user_password = bcrypt.generate_password_hash(
            request.form['user_password']
        ).decode('utf-8')
        _clear_session_except(['_flashes'])

        db = _get_database()
        cursor = db.cursor(buffered=True, dictionary=True)

        cursor.execute(
            f"UPDATE users SET user_password = '{new_user_password}' WHERE email = '{email}';")
        db.commit()
        cursor.close()

        return redirect(url_for('home.login'))

    return render_template("change_password.html")


@home_bp.route("/logout")
def logout():
    # Clear all stored data
    _clear_session_except([])
    return redirect(url_for('home.login'))




