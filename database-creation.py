"""
Create the database and its tables
"""

import pymysql
pymysql.install_as_MySQLdb()  # Install MySQL driver
import MySQLdb as my


# Connect to the localhost

db = my.connect(host="localhost", user="root", passwd="")

cursor = db.cursor()


# Create the database

sql = "CREATE DATABASE basketball_stats COLLATE 'utf8_general_ci'"

cursor.execute(sql)


# Commit the query

db.commit()


# Close the connection

db.close()


# Connect to the newly-created database

db = my.connect(host="localhost", user="root", passwd="", db="basketball_stats")

cursor = db.cursor()


# Create players table

sql = ("CREATE TABLE players "
       
       "(player_id MEDIUMINT(8) PRIMARY KEY, "
       "first_name VARCHAR(255), "
       "last_name VARCHAR(255), "
       "jersey_number TINYINT(3) UNSIGNED, "
       "position VARCHAR(5))")

cursor.execute(sql)


# Create teams table

sql = ("CREATE TABLE teams "
       
       "(team_id MEDIUMINT(8) PRIMARY KEY, "
       "city VARCHAR(255), "
       "name VARCHAR(255), "
       "abbreviation VARCHAR(3), "
       
       "UNIQUE KEY (abbreviation))")

cursor.execute(sql)


# Create matches table

sql = ("CREATE TABLE matches "
       
       "(match_id VARCHAR(20) PRIMARY KEY, "
       "date DATETIME, "
       "location VARCHAR(255))")

cursor.execute(sql)


# Create match_teams table

sql = ("CREATE TABLE match_teams "
       
       "(match_id VARCHAR(20), "
       "team_id MEDIUMINT(8), "

       "PRIMARY KEY (match_id, team_id), "
       "FOREIGN KEY (match_id) REFERENCES matches(match_id), "
       "FOREIGN KEY (team_id) REFERENCES teams(team_id))")

cursor.execute(sql)


# Create match_players table

sql = ("CREATE TABLE match_players "
       
       "(match_id VARCHAR(20), "
       "player_id MEDIUMINT(8), "
       "team_id MEDIUMINT(8), "

       "PRIMARY KEY (match_id, player_id), "
       "FOREIGN KEY (match_id) REFERENCES matches(match_id), "
       "FOREIGN KEY (player_id) REFERENCES players(player_id), "
       "FOREIGN KEY (team_id) REFERENCES teams(team_id))")

cursor.execute(sql)


# Create field_goal_attempts table


sql = ("CREATE TABLE field_goal_attempts "

       "(play_id INT(10), "
       "match_id VARCHAR(20), "
       "player_id MEDIUMINT(8), "
       "team_abbreviation VARCHAR(3), "
       "quarter TINYINT(1), "
       "time TIME, "
       "shot_type VARCHAR(100), "
       "distance_feet TINYINT(3), "
       "points TINYINT(1), "
       "x MEDIUMINT(5), "
       "y MEDIUMINT(5), "
       "outcome VARCHAR(20), "

       "PRIMARY KEY (play_id, match_id), "
       "FOREIGN KEY (match_id) REFERENCES matches(match_id), "
       "FOREIGN KEY (player_id) REFERENCES players(player_id), "
       "FOREIGN KEY (team_abbreviation) REFERENCES teams(abbreviation))")

cursor.execute(sql)


# Commit the query

db.commit()


# Close the connection

db.close()
