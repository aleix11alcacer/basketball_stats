import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb as my

from matplotlib.patches import Circle, Rectangle, Arc

def draw_court(ax=None, color='black', lw=1, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca(frame_on=False)

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop

    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system

    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, 0, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 139, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 139, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0.3, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


# Define the database conexion

conn = my.connect(host="localhost", user="root", passwd="", db="basketball_stats", charset="utf8")


# Consult team name

abbr = "'GSW'"

sql = ("select * "
       "from teams "
       "where abbreviation like " + abbr + " ")

team = pd.read_sql(sql, conn)


# Consult league field attemps

sql = ("select * "
       "from field_goal_attempts ")

league_shots = pd.read_sql(sql, conn)

x_l = []
y_l = []
c_l = []

for _, s in league_shots.iterrows():
    x = s['y']
    y = s['x']

    c = 0
    if s['outcome'] == 'SCORED':
        c = 1

    if y > 470:
        x = 500 - x
        y = 940 - y

    x_l.append(x)
    y_l.append(y)
    c_l.append(c)


# Consult player field attemps

sql = ("select * "
       "from field_goal_attempts "
       "where team_abbreviation like " + abbr + " ")

player_shots = pd.read_sql(sql, conn)

x_p = []
y_p = []
c_p = []

for _, s in player_shots.iterrows():
    x = s['y']
    y = s['x']

    c = 0
    if s['outcome'] == 'SCORED':
        c = 1

    if y > 470:
        x = 500 - x
        y = 940 - y

    x_p.append(x)
    y_p.append(y)
    c_p.append(c)


# Define the figure

dpi = 150
inch = 15
fig = plt.figure(figsize=(12, 12))

ax = fig.add_axes([0, 0, 1, 1], frame_on=False)

draw_court(ax, outer_lines=True)

ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
plt.xlim(-300, 300)
plt.ylim(-100, 500)

ax2 = plt.axes([.084, .088, .832, 0.782], frame_on=False)
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 470)
ax2.xaxis.set_visible(False)
ax2.yaxis.set_visible(False)
ax2.patch.set_alpha(0)


# Create the hexbin

ls_x = 25
ls_y = 27
x = np.linspace(0, 500, ls_x)
y = np.linspace(0, 470, ls_y)

xv, yv = np.meshgrid(x, y)


x_cte = (x[1]-x[0])
y_cte = (y[1]-y[2])

for i in range(len(xv)):
    if i % 2 == 0:
        xv[i] += x_cte/2


# Classify team data

t_data = np.zeros((ls_y, ls_x, 4))

for i in range(ls_y):
    for j in range(ls_x):
        t_data[i, j, 0] = xv[i, j]
        t_data[i, j, 1] = 470 - yv[i, j]

for x, y, c in zip(x_p, y_p, c_p):
    ux = int(x//x_cte)
    uy = int(y//y_cte)

    t_data[uy, ux, 2] += c
    t_data[uy, ux, 3] += 1


m = np.max(t_data[:, :, 3])

t_data = t_data.reshape(-1, 4)


# Classify league data

l_data = np.zeros((ls_y, ls_x, 4))

for i in range(ls_y):
    for j in range(ls_x):
        l_data[i, j, 0] = xv[i, j]
        l_data[i, j, 1] = 470 - yv[i, j]

for x, y, c in zip(x_l, y_l, c_l):
    ux = int(x//x_cte)
    uy = int(y//y_cte)

    l_data[uy, ux, 2] += c
    l_data[uy, ux, 3] += 1

l_data = l_data.reshape(-1, 4)


# Plot data

for (xp, yp, cp, tp), (xl, yl, cl, tl) in zip(t_data, l_data):
    if tp > 0:
        uxp = int(xp // x_cte)
        uyp = int(yp // y_cte)

        uxl = int(xl // x_cte)
        uyl = int(yl // y_cte)

        if tl != 0:
            l_avg = cl / tl
        else:
            l_avg = 0

        t_avg = cp / tp

        dif = t_avg - l_avg

        ms = 33
        redim = tp/m+(1-tp/m)*0.3

        if dif < -0.6:
            plt.plot(xp, yp, 'h', ms=ms*redim, color='#ffcccc')
        elif dif < -0.2:
            plt.plot(xp, yp, 'h', ms=ms*redim, color='#ff6666')
        elif dif < 0.2:
            plt.plot(xp, yp, 'h', ms=ms*redim, color='#ff0000')
        elif dif < -0.6:
            plt.plot(xp, yp, 'h', ms=ms*redim, color='#990000')
        else:
            plt.plot(xp, yp, 'h', ms=ms*redim, color='#330000')


# Insert text

ax.text(0, 460, "Shot Chart - 2016/17", verticalalignment="center", horizontalalignment="center", color="black",
        fontsize=25, fontweight="bold")

ax.text(0, 440, team['city'].values[0] + " " + team['name'].values[0], verticalalignment="center",
        horizontalalignment="center", color="black", fontsize=20)

ax.text(180, 400, "Efficiency", verticalalignment="center", horizontalalignment="center", color="black", fontsize=10)
ax.text(150, 380, "league <", verticalalignment="center", horizontalalignment="right", color="black", fontsize=10)
ax.plot(160, 380, 'h', ms=15, color='#ffcccc')
ax.plot(170, 380, 'h', ms=15, color='#ff6666')
ax.plot(180, 380, 'h', ms=15, color='#ff0000')
ax.plot(190, 380, 'h', ms=15, color='#990000')
ax.plot(200, 380, 'h', ms=15, color='#330000')
ax.text(210, 380, "> league", verticalalignment="center", horizontalalignment="left", color="black", fontsize=10)

ax.text(-200, 400, "Frequency", verticalalignment="center", horizontalalignment="center", color="black", fontsize=10)
ax.text(-220, 380, "low", verticalalignment="center", horizontalalignment="right", color="black", fontsize=10)
ax.plot(-213, 380, 'h', ms=9, color='#666666')
ax.plot(-203, 380, 'h', ms=15, color='#666666')
ax.plot(-190, 380, 'h', ms=21, color='#666666')
ax.text(-180, 380, "high", verticalalignment="center", horizontalalignment="left", color="black", fontsize=10)


# Save figure

file_path = ("results/hexbin.png")
directory = os.path.dirname(file_path)

if not os.path.exists(directory):
    os.makedirs(directory)

plt.savefig(file_path)
plt.close()
