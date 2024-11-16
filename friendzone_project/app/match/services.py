from flask import session, render_template, flash
from mysql.connector import Error
from mysql.connector.errors import IntegrityError
import random
from datetime import datetime

from friendzone_project.app.extensions import _get_database



def save_search_result():
    """Saves the search criteria to the search_criteria table."""

    search_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db = _get_database()
    cursor = db.cursor()

    select_query = """
        SELECT user_id FROM users
        WHERE user_name = %s
    """
    cursor.execute(select_query, [session.get('username')])

    result = cursor.fetchone()

    # Unpack the tuple to get the actual value
    if result:
        session['user_id'] = result[0]

    insert_query = """
    INSERT INTO search_criteria (user_id, latitude, longitude, location, radius, days, activity, time_block, search_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (session.get('user_id'), session.get('lat'), session.get('lon'), session.get('location'),
              session.get('db_radius'), session.get('days'), session.get('display_activity'), session.get('timeslot'), search_time)

    try:
        cursor.execute(insert_query, values)
        db.commit()
    except Error as e:
        print(f"Error saving result to database: {e}")

    finally:
        cursor.close()


def find_matches(user_id, activity, day, timeslot, lat, lon, radius):
    """Finds matching users based on search criteria using the Haversine formula."""
    db = _get_database()
    cursor = db.cursor(dictionary=True)

    try:
        # Find potential matches using the Haversine formula for distance
        select_query = """
            SELECT user_id,
               (6371000 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(latitude)) *
               COS(RADIANS(longitude) - RADIANS(%s)) +
               SIN(RADIANS(%s)) * SIN(RADIANS(latitude)))) AS distance
            FROM search_criteria
            WHERE user_id != %s
              AND activity = %s
              AND time_block = %s
              AND days = %s
            HAVING distance <= %s OR distance is NULL;
        """

        cursor.execute(select_query, (lat, lon, lat, user_id, activity, timeslot, day, radius))  # Using the radius in m not miles for Haversine Formula

        matched_users = cursor.fetchall()
        return matched_users

    except Exception as e:
        print(f"Error finding matches: {e}")
        return None

    finally:
        cursor.close()


def save_match(sender_id, receiver_id, activity, location):
    """ Saves the match details to the database."""
    db = _get_database()
    cursor = db.cursor()
    match_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        insert_query = """
            INSERT INTO user_matches (sender_id, receiver_id, location, activity, match_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (sender_id, receiver_id, location, activity, match_date))
        db.commit()
        return True

    except IntegrityError as e:
        print(f"Duplicate match error: {e}")
        return "duplicate"

    except Exception as e:
        print(f"Error saving match: {e}")
        return False

    finally:
        cursor.close()


def find_and_save_match():
    """Finds and saves a match if one is found."""
    user_id = session.get("user_id")
    activity = session.get("display_activity")
    day = session.get("days")
    timeslot = session.get("timeslot")
    lat = session.get("lat")
    lon = session.get("lon")
    radius = session.get("radius")
    location = session.get("location")

    # Find matches
    matched_users = find_matches(user_id, activity, day, timeslot, lat, lon, radius)

    if not matched_users:
        return render_template("no_match.html", data=session.get('latest_search'), activity=activity, location=location)

    # Randomly pick a match
    matched_user = random.choice(matched_users)["user_id"]
    session["matched_user"] = matched_user

    # Save the match
    save_result = save_match(user_id, matched_user, activity, location)

    if save_result == "duplicate":
        return render_template("dupe_match.html", data=session.get('latest_search'), activity=activity, location=location)
    elif save_result:
        return render_template("match_success.html", data=session.get('latest_search'), activity=activity, location=location)
    else:
        flash(f"Unexpected error during matching process: {e}", category='error')
        return render_template("no_match.html", data=session.get('latest_search'), activity=activity, location=location)
