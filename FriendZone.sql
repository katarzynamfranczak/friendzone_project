DROP DATABASE FriendZone;
CREATE DATABASE FriendZone;
USE FriendZone;
-- A table consisting of all users with login credentials for FriendZone:
CREATE TABLE Users (
  user_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, -- known to app admin
  user_name VARCHAR(20) UNIQUE NOT NULL,
  email VARCHAR(20) UNIQUE NOT NULL,
  user_password VARCHAR(10) NOT NULL, -- only accepts 10, not 9? *add in Python code: to be 9 characters long, upper, lower case, number, special character*
  user_type ENUM("admin", "user") NOT NULL,
  user_dob DATE NOT NULL, -- must be in the format: YYYY-MM-DD *instruction to be made in Python code*
  CONSTRAINT age_restriction CHECK (TIMESTAMPDIFF(YEAR, user_dob, SYSDATE()) >= 18)
);


INSERT INTO Users
VALUES
(1, "DesiP", "dp@mail.com", "password!", "admin", "2000-01-01"),
(2, "HannahC", "hc@mail.com", "password2", "admin", "1999-02-02"),
(3, "KatF", "kf@mail.com", "password3", "user", "1998-03-03"),
(4, "KoniB", "kb@mail.com", "password4)", "user", "1997-04-04"),
(5, "MahumK", "mk@mail.com", "password5", "user", "1996-05-05"),
(6, "MariaP", "mp@mail.com", "password6", "user", "1995-06-06"),
(7, "RahaT", "rt@mail.com", "password7", "user", "1995-07-07")
-- ("ID008", "SusanQ", "sq@mail.com", "password8", "user", "2010-08-08"); --this is a test of underaged user
;

CREATE TABLE Favourites (
    faves_id VARCHAR(8) PRIMARY KEY,
    user_id INTEGER NOT NULL,
	activity ENUM("Pub/bar", "Cinema", "Bakery") NOT NULL,
    latitude DECIMAL(11, 8),  -- Since latitude ranges from -180 to +180 (degrees), a DECIMAL(11,8) is appropriate.
    longitude DECIMAL(11, 8), -- Since longtitude ranges from -180 to +180 (degrees), a DECIMAL(11,8) is appropriate.
    time_block VARCHAR(9), -- Python code will need to present time block options e.g. 0900-1200...alt ENUM
    times DATETIME,
    venue_id VARCHAR(10) NOT NULL, -- if no review function, no need for venue_id, and remove from insert into also
    vegan BOOLEAN DEFAULT FALSE,
    gluten_free BOOLEAN DEFAULT FALSE,
    alcohol_free BOOLEAN DEFAULT FALSE,
    dog_friendly BOOLEAN DEFAULT FALSE,
	CONSTRAINT FK_Favourites_id FOREIGN KEY (user_id) REFERENCES Users (user_id)
    );

INSERT INTO Favourites (faves_id, user_id, activity, latitude, longitude, times, venue_id, vegan, gluten_free, alcohol_free, dog_friendly)
VALUES
("FAV00001", 1, "Cinema", 40.748817, -73.985428, "2024-11-16T14:30:00", "VENUE001", TRUE, TRUE, FALSE, TRUE);

CREATE TABLE Notification (
notification_id VARCHAR(8) PRIMARY KEY,
user_id INTEGER,
-- user_name VARCHAR(20) UNIQUE, -- discuss/explore: how to differentiate between the two users ...may not need if same notification to users
date_time TIMESTAMP,
notification VARCHAR(240) NOT NULL,
-- notification_read BOOLEAN NOT NULL), -- maybe a stretch: if there is a way to confirm/reject, then notify contact details
CONSTRAINT FK_Messages_uid FOREIGN KEY (user_id) REFERENCES Users (user_id)
-- CONSTRAINT FK_Messages_uname FOREIGN KEY (user_name) REFERENCES Users (user_name)
); -- possibly, this should be separate and instead have a sent? (/additionally)

select * from users where user_name = 'kf1';

SELECT * from users;
