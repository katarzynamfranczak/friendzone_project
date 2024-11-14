CREATE DATABASE FriendZone;
USE FriendZone;
-- A table consisting of all users with login credentials for FriendZone:
CREATE TABLE Users (
  UserId VARCHAR(5) PRIMARY KEY NOT NULL,
  UserName VARCHAR(20) NOT NULL,
  Email VARCHAR(20) NOT NULL,
  Password VARCHAR(8) NOT NULL),
  UserType VARCHAR(5) NOT NULL), 
  CHECK (UserAge>=18) -- A constraint to ensure users are at least 18 years of age to use the app. 
);

-- A table consisting of users' searches on FriendZone:
--  (NB Instead of FAVES, Search_Results)
CREATE TABLE Search_Results (
  UserId VARCHAR(5) FOREIGN KEY, 
  LatLon INT NOT NULL, -- needs to be from API
  Times NOT NULL, -- check Time format/if as timeblocks? 
  Activity VARCHAR NOT NULL), -- needs to be in line with API
  VenueId INT, -- unique, useful for later if adding data for REVIEWS
  Vegan BOOL,
  AlcoholFree BOOL, 
  DogFriendly BOOL
  );
  
  CREATE TABLE Messages (
  UserId VARCHAR(5) FOREIGN KEY NOT NULL, -- maybe mixing up my languages, but maybe have UserId as From_User?
  ToUser VARCHAR(20) NOT NULL, -- decide if this is UserID or as text? (text is more intuitive, UserId is cleaner?) ...alt: can use join to have both
  FromUser VARCHAR(20) NOT NULL,
  DateTime  -- check format type NOT NULL,
  Message VARCHAR(240) NOT NULL, 
  Read BOOL NOT NULL); --possibly, this should be separate and instead have a sent? (/additionally)

INSERT INTO Users
VALUES
(ID001, "DesiP", "dp@mail.com", "password1", "admin"),
(ID002, "HannahC", "hc@mail.com", "password2", "admin"),
(ID003, "KatF", "kf@mail.com", "password3", "user"),
(ID004, "KoniB", "kb@mail.com", "password4)", "user",
(ID005, "MahumK", "mk@mail.com", "password5", "user"),
(ID006, "MariaP", "mp@mail.com", "password6", "user"),
(ID007, "RahaT", "rt@mail.com", "password7"), "user";

INSERT INTO Search_Results
VALUES
-- UserId, Lat_Lon, Times, Activity, Venue_Id, Vegan, Alcohol_Free, Dog_Friendly
(ID001, ),
(ID002, , ),
(ID003, , ),
(ID004, , ),

INSERT INTO Messages
VALUES
(ID001, ID002, ID001, DateTime, "Message1", Y), 
(ID002, ID001, ID001, DateTime, "Message2", Y), 
(ID001, ID002, ID001, DateTime, "Message3", N);
