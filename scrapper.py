'''
Obtain data from .xml file to insert into database
'''

from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
import sys

import pymysql
pymysql.install_as_MySQLdb()  # Install MySQL driver
import MySQLdb as my


def send_request(url, game_id):

    if url == 'play-by-play':
        url = 'https://api.mysportsfeeds.com/v1.2/pull/nba/2016-2017-regular/game_playbyplay.xml'

    elif url == 'starting-lineup':
        url = 'https://api.mysportsfeeds.com/v1.2/pull/nba/2016-2017-regular/game_startinglineup.xml'

    try:
        response = requests.get(
            url,
            params={
                'gameid': game_id,
            },
            auth=('aleix11alcacer', '@leix96')
        )

        return response.content

    except requests.exceptions.RequestException:
        print('HTTP Request failed')


match_id = '20161026-OKL-PHI'

lup = send_request('starting-lineup', match_id)
pbp = send_request('play-by-play', match_id)


lup_beautiful = BeautifulSoup(lup, 'xml')
pbp_beautiful = BeautifulSoup(pbp, 'xml')


players = []
teams = []
matches = []

match_teams = []
match_players = []


date = pbp_beautiful.find('gam:game').find('date').text
location = pbp_beautiful.find('gam:game').find('location').text

matches.append([match_id, date, location])

for team in lup_beautiful.find_all('gam:teamLineup'):

    team_id = team.find('team').find('ID').text
    city = team.find('team').find('City').text
    name = team.find('team').find('Name').text
    abbreviation = team.find('team').find('Abbreviation').text

    teams.append([team_id, city, name, abbreviation])
    match_teams.append([match_id, team_id])

    for player in team.find('actual').find_all('gam:starter'):

        if player.find('gam:FirstName') is not None:

            player_id = player.find('gam:ID').text
            first_name = player.find('gam:FirstName').text
            last_name = player.find('gam:LastName').text
            jersey_number = player.find('gam:JerseyNumber').text
            position = player.find('gam:Position').text

            players.append([player_id, first_name, last_name, jersey_number, position])
            match_players.append([match_id, player_id, team_id])


field_goal_attempts = []

for i, fg in enumerate(pbp_beautiful.find_all('gam:fieldGoalAttempt')):

    play = fg.parent

    play_id = i
    player_id = fg.find('gam:shootingPlayer').find('gam:ID').text
    team_abbreviation = fg.find('gam:teamAbbreviation').text
    quarter = play.find('gam:quarter').text
    minutes, seconds = play.find('gam:time').text.split(':')
    time = '00:{:0>2s}:{:0>2s}'.format(minutes, seconds)
    shot_type = fg.find('gam:shotType').text
    distance_feet = fg.find('gam:distanceFeet').text
    points = fg.find('gam:Points').text
    x = fg.find('gam:shotLocation').find('gam:x').text
    y = fg.find('gam:shotLocation').find('gam:y').text
    outcome = fg.find('gam:outcome').text

    row = [play_id, match_id, player_id, team_abbreviation, quarter, time, shot_type, distance_feet, points, x, y,
           outcome]

    field_goal_attempts.append(row)


# Connect to the localhost

db = my.connect(host="localhost", user="root", passwd="", db="basketball_stats")

cursor = db.cursor()


# Add new players to "players" table

sql = ("INSERT IGNORE INTO players "
       "(player_id, first_name, last_name, jersey_number, position) "
       "VALUES (%s, %s, %s, %s, %s)")

cursor.executemany(sql, players)


# Add new teams to "teams" table

sql = ("INSERT IGNORE INTO teams "
       "(team_id, city, name, abbreviation) "
       "VALUES (%s, %s, %s, %s)")

cursor.executemany(sql, teams)


# Add new matches to "matches" table

sql = ("INSERT IGNORE INTO matches "
       "(match_id, date, location) "
       "VALUES (%s, %s, %s)")

cursor.executemany(sql, matches)


# Add the match teams to "match_teams" table

sql = ("INSERT IGNORE INTO match_teams "
       "(match_id, team_id) "
       "VALUES (%s, %s)")

cursor.executemany(sql, match_teams)


# Add the match players to "match_players" table

sql = ("INSERT IGNORE INTO match_players "
       "(match_id, player_id, team_id) "
       "VALUES (%s, %s, %s)")

cursor.executemany(sql, match_players)


# Add the field goal attempts  to "field_goal_attempts" table

sql = ("INSERT IGNORE INTO field_goal_attempts "
       "(play_id, match_id, player_id, team_abbreviation, quarter, time, shot_type, distance_feet, points, x, y,"
       "outcome) "
       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

cursor.executemany(sql, field_goal_attempts)


# Commit the query

db.commit()


# Close the connection

db.close()
