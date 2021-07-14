CREATE TABLE IF NOT EXISTS Business (
  business_id CHAR(22) PRIMARY KEY NOT NULL,
  business_name VARCHAR(70),
  adress VARCHAR(110),
  state CHAR(5),
  is_open BOOLEAN,
  stars NUMERIC(2, 1)
);

CREATE TABLE IF NOT EXISTS Users (
  user_id CHAR(22) PRIMARY KEY NOT NULL,
  user_name VARCHAR(40),
  review_count BIGINT,
  yelping_since TIMESTAMP,
  useful INT,
  funny INT,
  cool INT,
  fans INT,
  average_stars NUMERIC(3, 2)
);

CREATE TABLE IF NOT EXISTS Friend (
  user_id1 CHAR(22) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  user_id2 CHAR(22) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL
);

CREATE TABLE IF NOT EXISTS Review (
  review_id CHAR(22) PRIMARY KEY NOT NULL,
  user_id CHAR(22) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  business_id CHAR(22) REFERENCES Business(business_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  stars NUMERIC(2, 1) ,
  date TIMESTAMP,
  useful INT,
  funny INT,
  cool INT
);



CREATE TABLE IF NOT EXISTS Tip (
  tip_id INT GENERATED ALWAYS AS IDENTITY NOT NULL,
  tip_text VARCHAR(2000),
  date TIMESTAMP,
  compliment_count INT,
  business_id CHAR(22) REFERENCES Business(business_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  user_id CHAR(22) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL
);



COPY Business (business_id , business_name, adress , state , is_open , stars )
FROM '/Users/tolu/Downloads/yelp_academic_dataset/yelp_academic_dataset_business.csv'
DELIMITER ','
CSV HEADER
;


COPY Users ( user_id , user_name ,review_count ,yelping_since , useful ,funny ,cool ,fans ,average_stars )
FROM '/Users/tolu/Downloads/yelp_academic_dataset/yelp_academic_dataset_user.csv'
DELIMITER ','
CSV HEADER
;


COPY Friend (user_id1 , user_id2 )
FROM '/Users/tolu/Downloads/yelp_academic_dataset/yelp_academic_dataset_friend.csv'
DELIMITER ','
CSV HEADER
;


COPY Review (review_id , user_id ,business_id , stars  ,date , useful , funny , cool )
FROM '/Users/tolu/Downloads/yelp_academic_dataset/yelp_academic_dataset_reviewNoText.csv'
DELIMITER ','
CSV HEADER;

COPY Tip (tip_text , date ,compliment_count, business_id ,user_id )
FROM '/Users/tolu/Downloads/yelp_academic_dataset/yelp_academic_dataset_tip.csv'
DELIMITER ','
CSV HEADER;
