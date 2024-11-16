# CFG-Group-2-Project  
Our Lovely Project  
  
# Set Up  
In order to install the necessary python libraries, you would need to install them from `requirements.txt` using the following command:  
  
`pip install -r requirements.txt`  
  
1) Add API keys into credentials.py Keys have been sent in Slack  
2) Run meetup.py  
3) Run client.py  
4) utils_oop.py has the main functionality of the search feature  
  
  
## Raha 15/11  
# I have amended Hannah's code to include the green and orange section of the diagram (saving search results and matching users)  
# For the code to work the test database I created based on Mahum & Desi's code needs to be used   
  
### As per above set up instructions & In addition  
5) db_helpers.py include all of the database related functions which are referenced in utils_oop.py  
  
  
# Hannah 16/11  
 - meetup.py (get-location_info_api): Deleted some unnecessary test lines I'd previously left in accidentally  
 - credentials.py: Added variables for db connections  
 - FriendZoneTest.sql: Added a UNIQUE constraint to "Email" on the USERS table  
 - db_helpers.py: Imported db credentials and tweaked connection command.   
   - Line 90 (find_and_save-match): edited formatting  
 - utils_oop.py (user_input): Lines 231/232/239/241/246/247/363 tweaked to reduce duplication.   
   - Line 249 added a way to shorten activity name to add to db  
   - Line 345 (get info): added a way to check location is valid before moving on

