import mysql.connector
from mysql.connector import Error
import random
from credentials import HOST, USER, PASSWORD, DATABASE


def create_database_connection():
    """Connects to the FriendZone database."""
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,       # Replace with your database username
            password=PASSWORD,        # Replace with your database password
            database=DATABASE
        )

        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def save_search_result(user_id, lat_lon, times, activity, name, address, website, opening_hours, timeslot, day): # Hannah: added variables to be passed
    """Saves a simplified search result to the Search_Results table."""
    connection = create_database_connection()
    if connection is None:
        print("Failed to connect to database.")
        return

    cursor = connection.cursor()
    insert_query = """
    INSERT INTO Search_Results (UserId, LatLon, Times, Activity, VenueName, Address, Website, OpeningHours, VisitTime, VisitDay) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """ # Hannah: added variables to be passed (but not yet on DB)
    values = (user_id, lat_lon, times, activity, name, address, website, opening_hours, timeslot, day) # Hannah: added variables to be passed

    try:
        cursor.execute(insert_query, values)
        connection.commit()
    except Error as e:
        print(f"Error saving result to database: {e}")
    finally:
        cursor.close()
        connection.close()


def find_and_save_match(user_id, activity, venues, search_date): # Hannah: need to add specific time/day matches now :)
    """
    Finds and saves a match for a user based on shared activity and any overlapping venue.
    """
    connection = create_database_connection()
    if connection is None:
        print("Database connection error.")
        return

    cursor = connection.cursor(dictionary=True)

    # Use a list to collect potential matches for any venue in `venues`
    potential_matches = []

    for venue_name in venues:
        select_query = """
            SELECT UserId FROM Search_Results
            WHERE UserId != %s AND Activity = %s AND VenueName = %s AND DATE(Times) = %s
        """
        cursor.execute(select_query, (user_id, activity, venue_name, search_date))
        results = cursor.fetchall()
        potential_matches.extend([match["UserId"] for match in results])

    if not potential_matches:
        print("No matches found.")
        return

    matched_user = random.choice(potential_matches)

    # Insert only if this match does not already exist
    insert_query = """
        INSERT INTO User_Matches (User1Id, User2Id, Activity, VenueName, MatchDate)
        SELECT %s, %s, %s, %s, %s FROM DUAL
        WHERE NOT EXISTS (
            SELECT 1 FROM User_Matches 
            WHERE (User1Id = %s AND User2Id = %s AND Activity = %s AND VenueName = %s AND MatchDate = %s)
               OR (User1Id = %s AND User2Id = %s AND Activity = %s AND VenueName = %s AND MatchDate = %s)
        )
    """
    cursor.execute(insert_query, (user_id, matched_user, activity, venue_name, search_date,
                                  user_id, matched_user, activity, venue_name, search_date,
                                  matched_user, user_id, activity, venue_name, search_date))
    connection.commit()
    print(f"\nMatched with User ID:  {matched_user}   for activity:   {activity}  at venue(s): \n\n {', '.join(venues)}.") # Hannah: just added a couple of \n for ease of readability

    cursor.close()
    connection.close()