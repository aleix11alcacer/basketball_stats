from flask import Flask, request, redirect, url_for, render_template
from matplotlib.patches import Circle, Rectangle, Arc

import matplotlib.pyplot as plt

import requests

import numpy as np
import pandas as pd

import io
import base64


def draw_court(ax=None, color='black', lw=1, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca(frame_on=False)

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop

    # Diameter of a hoop is 18" so it has a radius of 9", which is a value 7.5 in our coordinate system

    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, 0, linewidth=lw, color=color)

    # Create the outer box of the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)

    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)

    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='--')

    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)

    # Three point line

    # Create the side 3pt lines, they are 14ft long before they begin to arc

    corner_three_a = Rectangle((-220, -47.5), 0, 138, linewidth=lw, color=color)

    corner_three_b = Rectangle((220, -47.5), 0, 138, linewidth=lw, color=color)

    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop

    three_arc = Arc((0.3, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)

    # Center Court

    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)

    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw, restricted,
                      corner_three_a, corner_three_b, three_arc]


    # Draw the half court line, baseline and side out bound lines

    outer_line_b = Rectangle((-250, -47.5), 500, 0, linewidth=lw, color=color, fill=False)
    outer_line_l = Rectangle((-250, -47.5), 0, 380, linewidth=lw, color=color, fill=False)
    outer_line_r = Rectangle((250, -47.5), 0, 380, linewidth=lw, color=color, fill=False)

    court_elements += [outer_line_b, outer_line_l, outer_line_r]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

def get_roster(season='2017-18', team_id=''):

    url = 'http://stats.nba.com/stats/commonteamroster'

    try:
        response = requests.get(
            url,
            params={
                'Season': season,
                'TeamID': team_id,
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
            }
        )

        return response

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def send_request(season='2017-18', season_type='Regular Season', team_id='0', player_id='0', game_id='', outcome='',
                 location='', month='0', season_segment='', date_from='', date_to='', oponent_team_id='0',
                 vs_conference='', vs_division='', player_position='', rookie_year='', game_segment='', period='0',
                 last_n_games='0', context_measure='FGA'):

    url = 'http://stats.nba.com/stats/shotchartdetail'

    try:
        response = requests.get(
            url,
            params={
                'Season': season,
                'SeasonType': season_type,
                'TeamID': team_id,
                'PlayerID': player_id,
                'GameID': game_id,
                'Outcome': outcome,
                'Location': location,
                'Month': month,
                'SeasonSegment': season_segment,
                'DateFrom': date_from,
                'DateTo': date_to,
                'OpponentTeamID': oponent_team_id,
                'VsConference': vs_conference,
                'VsDivision': vs_division,
                'PlayerPosition': player_position,
                'RookieYear': rookie_year,
                'GameSegment': game_segment,
                'Period': period,
                'LastNGames': last_n_games,
                'ContextMeasure': context_measure,
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
            }
        )

        return response

    except requests.exceptions.RequestException:
        print('HTTP Request failed')


teams_id = {'Hawks': 1610612737, 'Celtics': 1610612738, 'Nets': 1610612751, 'Hornets': 1610612766, 'Bulls': 1610612741,
            'Cavaliers': 1610612739, 'Mavericks': 1610612742, 'Nuggets': 1610612743, 'Pistons': 1610612765,
            'Warriors': 1610612744, 'Rockets': 1610612745, 'Pacers': 1610612754, 'Clippers': 1610612746,
            'Lakers': 1610612747, 'Grizzlies': 1610612763, 'Heat': 1610612748, 'Bucks': 1610612749,
            'Timberwolves': 1610612750, 'Pelicans': 1610612740, 'Knicks': 1610612752, 'Thunder': 1610612760,
            'Magic': 1610612753, '76ers': 1610612755, 'Suns': 1610612756, 'Blazers': 1610612757,
            'Kings': 1610612758,
            'Spurs': 1610612759, 'Raptors': 1610612761, 'Jazz': 1610612762, 'Wizards': 1610612764}

players_id = {}

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def get_team():
    if request.method == 'POST':

        team_abb = request.form['team']
        team_id = teams_id[team_abb]
        season = request.form['season']

        return redirect(url_for('get_player', season=season, team_id=team_id))

    else:
        return render_template('team.html', teams=sorted(teams_id.keys()))


@app.route('/get_player', methods=['POST', 'GET'])
def get_player():

    season = request.args['season']
    team_id = request.args['team_id']

    if request.method == 'POST':
        player_name = request.form['player_name']
        player_id = players_id[player_name]

        return redirect(url_for('plot_shot', season=season, player_id=player_id))
    else:

        resp = get_roster(team_id=team_id, season=season)

        roster_data = resp.json()['resultSets'][0]['rowSet']
        roster_headers = resp.json()['resultSets'][0]['headers']

        roster_players = pd.DataFrame(roster_data, columns=roster_headers)

        players_id.clear()
        for _, player in roster_players.iterrows():
            players_id[player['PLAYER']] = player['PLAYER_ID']

        return render_template('player.html', players=sorted(players_id.keys()), season=season, team_id=team_id)


@app.route('/shot-chart', methods=['POST', 'GET'])
def plot_shot():

    season = request.args['season']
    player_id = request.args['player_id']

    if request.method == 'POST':
        return redirect(url_for('get_team'))

    else:
        img = io.BytesIO()

        resp = send_request(player_id=player_id, season=season)
        # Define the figure

        dpi = 150
        inch = 15
        fig = plt.figure(figsize=(16, 12))

        ax = fig.add_axes([0, 0, 1, 1], frame_on=False)

        draw_court(ax, outer_lines=True)

        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_xlim(-350, 350)
        ax.set_ylim(-100, 420)

        ax2 = plt.axes([.143, .1, .71, 0.9], frame_on=False)
        ax2.set_xlim(-245, 245)
        ax2.set_ylim(-20, 450)
        ax2.xaxis.set_visible(False)
        ax2.yaxis.set_visible(False)
        ax2.patch.set_alpha(0)

        # Create the hexbin

        ls_x = 30
        ls_y = 32

        x = np.linspace(-245, 245, ls_x)
        y = np.linspace(-20, 450, ls_y)

        xv, yv = np.meshgrid(x, y)

        cte_x = (x[1] - x[0])
        cte_y = (y[1] - y[0])

        for i in range(len(xv)):
            if i % 2 == 0:
                xv[i] += cte_x / 2

        hexbin = np.zeros((ls_y, ls_x, 5))

        for i in range(ls_y):
            for j in range(ls_x):
                hexbin[i, j, 0] = xv[i, j]
                hexbin[i, j, 1] = 400 - yv[i, j]

        # Get league shot averages

        league_data = resp.json()['resultSets'][1]['rowSet']
        league_headers = resp.json()['resultSets'][1]['headers']

        league_averages = pd.DataFrame(league_data, columns=league_headers)

        league_AVG = {}
        relationate_keys = {}

        for _, zone in league_averages.iterrows():
            key = (zone['SHOT_ZONE_BASIC'], zone['SHOT_ZONE_AREA'], zone['SHOT_ZONE_RANGE'])
            if key not in relationate_keys:
                relationate_keys[key] = len(relationate_keys)
            key = relationate_keys[key]
            league_AVG[key] = zone['FG_PCT']

        # Get player shots and calculate player shot averages

        player_name = resp.json()['resultSets'][0]['rowSet'][0][4]

        player_data = resp.json()['resultSets'][0]['rowSet']
        player_headers = resp.json()['resultSets'][0]['headers']

        player_shots = pd.DataFrame(player_data, columns=player_headers)

        shots = pd.DataFrame(index=['x', 'y', 'flag', 'key'])

        player_FGA = {}
        player_FGM = {}

        for _, shot in player_shots.iterrows():
            x = shot['LOC_X']
            y = shot['LOC_Y']
            flag = shot['SHOT_MADE_FLAG']
            key = (shot['SHOT_ZONE_BASIC'], shot['SHOT_ZONE_AREA'], shot['SHOT_ZONE_RANGE'])

            key = relationate_keys[key]

            if y < 400:

                if key in player_FGA:
                    player_FGA[key] += 1
                    player_FGM[key] += flag
                else:
                    player_FGA[key] = 1
                    player_FGM[key] = flag

                ux = int((x + 250) // cte_x)
                uy = int((400 - y) // cte_y)

                hexbin[uy, ux, 2] += flag
                hexbin[uy, ux, 3] += 1
                hexbin[uy, ux, 4] = key

        max_shot = np.max(hexbin[:, :, 3])

        hexbin = hexbin.reshape(-1, 5)

        player_AVG = {}

        for (k1, v1), (k2, v2) in zip(player_FGM.items(), player_FGA.items()):
            player_AVG[k1] = v1 / v2

        # Plot data

        for i, (x, y, ms, ts, key) in enumerate(hexbin):

            if ts > 0:

                avg_p = player_AVG[key]
                avg_l = league_AVG[key]

                dif = avg_p - avg_l

                marker_size = 30
                normalize = np.log(ts) / np.log(max_shot)

                if dif < -0.1:
                    plt.plot(x, y, 'h', ms=marker_size * normalize, color='#ffcccc')
                elif dif < -0.03:
                    plt.plot(x, y, 'h', ms=marker_size * normalize, color='#ff6666')
                elif dif < 0.03:
                    plt.plot(x, y, 'h', ms=marker_size * normalize, color='#ff0000')
                elif dif < 0.1:
                    plt.plot(x, y, 'h', ms=marker_size * normalize, color='#990000')
                else:
                    plt.plot(x, y, 'h', ms=marker_size * normalize, color='#330000')

        # Insert text

        ax2.text(0, 390, "NBA Shot Chart", verticalalignment="center", horizontalalignment="center", color="black",
                 fontsize=30, fontweight="bold")

        ax2.text(0, 370, "{0} ({1})".format(player_name, season), verticalalignment="center",
                 horizontalalignment="center", color="black", fontsize=20)

        ax2.text(180, 360, "Efficiency", verticalalignment="center", horizontalalignment="center", color="black",
                 fontsize=13)
        ax2.text(150, 340, "league <", verticalalignment="center", horizontalalignment="right", color="black", fontsize=10)
        ax2.plot(160, 340, 'h', ms=15, color='#ffcccc')
        ax2.plot(170, 340, 'h', ms=15, color='#ff6666')
        ax2.plot(180, 340, 'h', ms=15, color='#ff0000')
        ax2.plot(190, 340, 'h', ms=15, color='#990000')
        ax2.plot(200, 340, 'h', ms=15, color='#330000')
        ax2.text(210, 340, "> league", verticalalignment="center", horizontalalignment="left", color="black", fontsize=10)

        ax2.text(-200, 360, "Frequency", verticalalignment="center", horizontalalignment="center", color="black",
                 fontsize=13)
        ax2.text(-220, 340, "low", verticalalignment="center", horizontalalignment="right", color="black", fontsize=10)
        ax2.plot(-213, 340, 'h', ms=9, color='#666666')
        ax2.plot(-203, 340, 'h', ms=15, color='#666666')
        ax2.plot(-190, 340, 'h', ms=21, color='#666666')
        ax2.text(-180, 340, "high", verticalalignment="center", horizontalalignment="left", color="black", fontsize=10)

        # Save figure

        plt.savefig(img, format='png')
        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template('shot-chart.html', plot_url=plot_url, season=season, player_id=player_id)


if __name__ == '__main__':
    app.debug = True
    app.run()