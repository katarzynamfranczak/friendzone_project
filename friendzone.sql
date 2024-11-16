DROP DATABASE IF EXISTS FriendZone;
CREATE DATABASE FriendZone;
USE FriendZone;

-- A table consisting of all users with login credentials for FriendZone:
CREATE TABLE Users (
  user_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, -- known to app admin
  user_name VARCHAR(20) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  user_password VARCHAR(255) NOT NULL, -- at least 9 chars handled in Python
  user_type ENUM('admin', 'user') NOT NULL,
  user_dob DATE NOT NULL, -- must be in the format: YYYY-MM-DD *instruction to be made in Python code*
  CONSTRAINT age_restriction CHECK (TIMESTAMPDIFF(YEAR, user_dob, SYSDATE()) >= 18)
);

-- Insert users including salted hash of passwords
INSERT INTO users
VALUES
(001, 'DesiP', 'desi@mail.com', '$2b$12$2hsnKo8GvuQVVxLNRpcqm.RoS4WGurWlNMKhqmRN.CmqBf8sDjpbm', 'admin', '1990-01-01'), -- Password1
(002, 'HannahC', 'hannah@mail.com', '$2b$12$TB0etcVieCq0X87YlQv49e0bLY567myvell9ewIgdI5vQNfvykNC.', 'admin', '1991-02-02'), -- Password2
(003, 'KatF', 'kat@mail.com', '$2b$12$sAqpRA6yx.J19huBCCU8S.UdRt.p03U54b8IWJpbt2P/3DxmJw7p.', 'admin', '1992-03-03'), -- Password3
(004, 'KoniB', 'koni@mail.com', '$2b$12$UHV0ae2ShagIiaYc5ooyouoklgfrXGZYvvV1OxDTeAeufYcw47v06', 'user', '1993-04-04'), -- Password4
(005, 'MahumK', 'mahum@mail.com', '$2b$12$Gs3s6Kx.LAk4pV/NoBgoOeKLX7Myjl9bXMLuWs3sSL2DlQ7akyqzm', 'user', '1994-05-05'), -- Password5
(006, 'MariaP', 'maria@mail.com', '$2b$12$joK2XsZ48j86yyRMXDr7Jue8NyEbgQq34Zp7D44zGLJyae2wgl5qa', 'user', '1995-06-06'), -- Password6
(007, 'RahaT', 'raha@mail.com', '$2b$12$632.vD5qcxeUlCBDk7xa/u/Vdf./Xz6NuHuBl/140GpwyPEg28qUW', 'user', '1996-07-07'); -- Password7
-- ('008', 'SusanQ', 'sq@mail.com', '$2b$12$ECrXmjQ79tdVtJXgk2WKT.uGBIzJGn86MPDOI8mEyDzcQBUnMtRYm', 'user', '2010-08-08'); --this is a test of underaged user: Password8


CREATE TABLE search_criteria (
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
	activity ENUM ('Bar', 'Cinema', 'Bakery','Coffee Shop') NOT NULL, -- a,b,c, d *check if in line with python options, consider analytics for later
    latitude DECIMAL(11, 8),  -- Since latitude ranges from -180 to +180 (degrees), a DECIMAL(11,8) is appropriate.
    longitude DECIMAL(11, 8), -- Since longtitude ranges from -180 to +180 (degrees), a DECIMAL(11,8) is appropriate.
    location VARCHAR(20),
    days ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Weekdays', 'Weekends') NOT NULL,
	-- day_group ENUM('Weekdays', 'Weekends') DEFAULT NULL, -- removed to align with Python code
    radius ENUM ('1', '3', '5') NOT NULL,
    time_block ENUM('9:00 - 12:00', '12:00 - 15:00', '15:00 - 18:00', '18:00 - 21:00') NOT NULL, -- Python code will need to present time block options e.g. 0900-1200...alt ENUM
    search_time DATETIME,
    -- vegan BOOLEAN DEFAULT FALSE, -- Not available for the activities in our pilot app
    -- gluten_free BOOLEAN DEFAULT FALSE,
	CONSTRAINT FK_Search_criteria_id FOREIGN KEY (user_id) REFERENCES Users (user_id)
    );


-- with greater capacity/ to improve: could have more filters e.g. vegetarian, could incorporate venue_id for review function
INSERT INTO search_criteria (search_id, user_id, latitude, longitude, location, radius, days, activity, time_block, search_time)
VALUES
('001', 001, 51.37130490, -0.10195700, 'Croydon', '3', 'Monday', 'Bar', '12:00 - 15:00', '2024-11-16 14:30:00');


CREATE TABLE user_matches (
match_id INT AUTO_INCREMENT PRIMARY KEY,
sender_id INT NOT NULL,
receiver_id INT NOT NULL,
activity VARCHAR(50),
location VARCHAR(100),
match_date DATETIME,
-- message_text VARCHAR(240), -- Redundant at the moment
-- is_notification BOOLEAN DEFAULT FALSE,
-- is_match BOOLEAN DEFAULT FALSE,
-- date_time VARCHAR(20),
FOREIGN KEY (sender_id) REFERENCES Users(user_id),
FOREIGN KEY (receiver_id) REFERENCES Users(user_id));


CREATE TABLE messages (
message_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
sender_id INT NOT NULL,
receiver_id INT NOT NULL,
date_time TIMESTAMP,
message VARCHAR(240) NOT NULL,
isRead BOOL NOT NULL, -- Redundant column at the moment
FOREIGN KEY (sender_id) REFERENCES Users(user_id),
FOREIGN KEY (receiver_id) REFERENCES Users(user_id));

-- Store encrypted messages
INSERT INTO messages
VALUES
(001, 1, 2, '2024-11-27 10:30:00', 'Rk)cKhoorcwkhuhcPucZroi?', FALSE),
(002, 2, 1, '2024-11-27 11:00:00', 'Kl)cqlfhcwrcphhwc/rx?', TRUE),
(003, 1, 3, '2024-11-27 12:15:00', 'Rkcjrvk)cL pch!flwhgczhcpdwfkhg?', FALSE),
(004, 1, 2, '2024-11-27 10:30:00', 'Zrxogc/rxcolnhcwrcphhwcqh!wczhhncirucdcfriihh;', FALSE),
(005, 3, 2, '2024-11-27 11:00:00', 'Wklvclvcvxfkcdcjuhdwclghdcirucdqcdss?', TRUE);



-- Evolution of tables
-- Would possibly have added individual venues into our list in the future

/*
    CREATE TABLE User_Interactions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id VARCHAR(5) NOT NULL,
    receiver_id VARCHAR(5) NOT NULL,
    activity VARCHAR(50),
    venue_name VARCHAR(100),
    interaction_date TIMESTAMP,
    message_text VARCHAR(240),
    is_notification BOOLEAN DEFAULT FALSE,
    is_match BOOLEAN DEFAULT FALSE,
    date_time TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id));



    CREATE TABLE Venue (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    search_id VARCHAR(10) NOT NULL,
    venue_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    rating DECIMAL(3,2),
    contact_info VARCHAR(100),
    opening_hours TEXT,
    CONSTRAINT FK_Search FOREIGN KEY (search_id) REFERENCES Searches(search_id));
    */