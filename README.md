# FriendZone Project
A platonic meet up app to make new friends.
The FriendZone database has been built to support our social networking app designed to connect users based on shared activities, availability, and location-based criteria. 
It offers functionalities for managing users, activity tracking, and messaging facilitation.

- [GitHub Structure](#github-structure)
- [Set up](#set-up)
- [About the Structure](#about-the-structure)
- [Feature - Login / Logout](#login--logout-kat)
- [Feature - Search](#search-hannah)
- [Feature - Match](#match-raha)
- [Feature - Messages](#messages-maria)
- [Feature - Admin](#admin-kat)
- [Database](#database-desi--mahum)
- [Extensions](#extensions-hannah--kat)
- [Testing](#testing-all-but-raha--koni-leading)
- [Future Developments](#future-developments)
- [Lessons Learned](#lessons-learned)
- [Links](#links)

# GitHub Structure
- The final project / application code is contained within the **main** branch.
- In order to easily showcase the work that has gone into each feature we have chosen to leave the database and feature/ branches active.


# Set Up
In order to install the necessary python libraries, you need to install them from `requirements.txt` using the following command:

`pip install -r requirements.txt`

1) In your db client, execute the SQL code in **friendzone.sql** to set up the database. _The database is already integrated with the application Python code_
2) Add your API keys & database credentials into **my_flask_app/config.py**. If you need to create your own API keys, please refer to this section: [Creating API Keys](#creating-api-keys) **_Assessment Keys,  credentials & suggested web-interface explorations have been sent via Slack_**
3) At the moment FriendZone is being piloted within the UK, so please leave the country set as UK.
4) Run **run.py**
5) Click the hyperlink created to open the web interface

## About the Structure
- In order to facilitate a clean directory structure and an engaging user experience, we chose to use Flask with Jinja2
templates, and organised them by using the Flask Blueprints concept for organisation.
- Each feature has its own blueprint, which consists of an __init__.py to initialise the blueprint and routes.py to define
the api routes. Depending on the feature it may also have a services.py file which holds the functions unique to that feature. 
None of the features have a models.py file in this application, as it was not required.
- The static and template directories hold the shared html, css and images files. The html templates are somewhat 
influenced by session variables, particularly 'username', 'user_type', '_flashes' and a few password validity variables.
- app/extensions.py contains the shared utils - db connection functions and session clearing.
- Initially some of this code was written to work in a console app, it has been amended to suit a web application.

## Login / Logout (Kat)
- /home: This route will clear the session cache of unnecessary data. Sessions currently last a max. of 30 mins.
- /login: Validates user password matches the stored hash in the db & stores session variables for later use.
- /signup: Validates user password meets requirements, that user is over age & user does not yet exist.
- /change_password: Permits user to change password based on their registered email address.
- /logout: Clear all session data and redirect to log in page.

## Search (Hannah)
- /search: Extracts data from form and queries 2 external APIs _(locationiq & Here Geocoding & Search)_ to get a list of matching venues. 
  - Formats responses and filters based on searched criteria to display final results on web page.
  - Gives user the option to save their criteria and look for a matching user search, or search again.
- _note: all API endpoints are inaccessible will redirect to /login if the user is currently not logged in._

## Match (Raha)
- /match: Takes search criteria and saves it to the search_criteria table.
  - Queries search_criteria to find another user who has run a similar query, based on: the activity type, time, day and radius of the location.
  - If no match found, the user is given the option to search again. 
  - If a match is found, the user is informed and given the chance to message the match. This match is saved to user_matches table.
  - If user already has a match at that day and time, user is informed and no new match is recorded.

## Messages (Maria)
- /messages: Displays all messaged received by the currently logged-in user.
- /thread: Displays all messages between currently logged-in user and one other - both sent and received.
- /delete: Allows user to delete current message thread.
- /reply: Allows currently logged-in user to respond to an active thread.
- _note: Messages can only be sent via the app, the logged-in user has no way to amend the receiver of the message. This is to make sure only matched users can communicate._
- _note: All messages are encrypted before being stored in the messages table of the db, and decrypted before displaying on the webpage_

## Admin (Kat)
- /admin: Admins can view all registered users and delete or promote other users to become Admins.
- /promote_to_admin: Promote a standard user to Admin.
- /delete_user: Delete a user from FriendZone app. Not possible if user has already matched, saved a search or sent/received a message.

## Database (Desi & Mahum)
- users: Users & login credentials including password hash, with an age check constraint (Over 18)
- search_criteria: Store all search criteria for later matching (if selected by user). Stores human-readable location as well as lat / lon for later analytics.
- user_matches: Stores successful matches based on search criteria.
- messages: Stores all messages to and from users.

## Extensions (Hannah & Kat)
- _clear_session_except: Clears all session variables, except those specified in a list.
- _get_current_user: Checks whether user is already logged in.
- _get_database: Checks whether db connection is active, if not calls _connect_to_database.
- _connect_to_database: Connects to database.

## Testing (All, but Raha & Koni leading)
Given our time constraints to deliver this project, we prioritised testing the core functionalities of our application (as outlined in our project documentation) to ensure its critical features were robust and reliable. 
- Testing was performed by different group members as follows:
  
**Hannah:**  
  Web-based functionality, focusing on features such as user authentication, activity search, location management, session handling, and password validation.
  Tests validated the application’s integration with external APIs, including accurate retrieval of geolocation data, activity searches, and secure database interactions.
  Key highlights include:
  - Ensuring valid and invalid user inputs for activities, locations, and dropdown options.
  - Testing password strength requirements
  - Verifying user authentication processes, such as database checks for valid accounts and session variable management
_Test suite can be found in the [friendzone_project/tests](friendzone_project/tests) subfolder on the main branch._
  
**Raha & Koni:**  
  Our test cases validate the legacy console-based functionality. While no longer actively used, these tests are retained as evidence of the development process and testing rigor.
  Our unit tests touched upon the following domains: 
  - user input and interaction flow 
  - database interaction
  - helper functions
  - API endpoints and responses
  - messaging and encryption
  - user authentication
_Our test suite can be found in the folder [feature/search_save_match/tests](feature/search-save-match/tests) within the save_search_match branch._

## Future Developments
- LOGIN: 
  - Add more complex password requirements.
  - Add MFA, including for password reset - possibly a reset link sent to registered email.
- SEARCH:
  - Would like to add in more criteria and activities (restaurants, swimming, vegan, gluten-free, dog-friendly etc)
- MESSAGES:
  - Currently isRead column is redundant - would create a function that changes this flag, based on interaction.
- ADMIN:
  - Would have a DEACTIVATE USER option, can be triggered by Admins or by the user themselves, marks them as not active, 
  no longer matchable, and can later be removed completely. Would need a stored procedure to remove the user id from 
  user_matches, messages & search_criteria tables as well.
- OTHER
  - Reviews of venues and activities
  
## Lessons Learned
- The Here Geocoding & Search API is great from our testing perspective, but if this application were to go into production we would 
perhaps need to seek out a more comprehensive API, possibly FourSquare or one of the other paid APIs that we initially researched.
- HerePlaces database is not as up to date or comprehensive in less densely populated areas.

## Links
- [Project Activity Log](https://docs.google.com/spreadsheets/d/1Lms-FDuU9wzIId0LlwbqzXFdXyLnC96b/edit?usp=sharing&ouid=104613648409604300723&rtpof=true&sd=true)
- [Gantt Chart](https://docs.google.com/spreadsheets/d/1eISBiEDjpTiGUsyN9ScjKlbIDUHHtHy5/edit?usp=sharing&ouid=104613648409604300723&rtpof=true&sd=true)
- [Project Meeting Minutes](https://docs.google.com/document/d/1PXTMPtxjRt3Va8b1DWj-WQEPy2LsndVUjHQObenWhTw/edit?tab=t.0#heading=h.wej4p4tw2436)
- [Application Architecture Diagram](https://drive.google.com/file/d/1VKvJ2IzYZ_x-LlyzO9alSOk9qtZrLwEA/view?usp=sharing)
- [Documentation](https://drive.google.com/file/d/1RcWAoRzJ7X57sUO2JWimhqj7_1blrN-M/view?usp=sharing)
- [Video Demos](https://drive.google.com/drive/folders/1oeGyox5S5sIvGqiY-vLs0qlTH1KcDiWY?usp=sharing)

## Creating API Keys
# Here Geocoding & Search 
_(**HP_KEY** in our config.py file)_([^1])

- Sign in to the [HERE](https://platform.here.com/) platform using your HERE account.
- Select the Access Manager from the launcher.
- Select the Apps tab and click Register new app.
- Enter a name for the app.
- Click Register. The HERE platform creates a new app with a unique app ID.
- On the Credentials tab, select API Keys and then click Create API key to generate a maximum of two API Keys for your application authentication credentials. The API key is created and displayed.

# LocationIQ 
_(**LOC_KEY** in our config.py file)_([^2])
- Login or Signup to the LocationIQ dashboard here: https://my.locationiq.com/dashboard/login
- Once you've logged in, please navigate to the 'API Access Tokens' tab to get your access token/ API key

[^1]: https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics/quick-start.html

[^2]: https://help.locationiq.com/support/solutions/articles/36000172496-how-do-i-get-the-api-key-access-token-
