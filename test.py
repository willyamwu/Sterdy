from cProfile import label
import time
from turtle import home
from nba_api.stats.static import teams
import json
import math
import re
import os
from nba_api.stats.static import players
import requests
import numpy as np
import CONSTANTS
from nba_api.stats.endpoints import LeagueGameFinder
from dotenv import load_dotenv
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import LeagueGameFinder, BoxScoreTraditionalV3, PlayerGameLog, CommonPlayerInfo, BoxScoreSummaryV2, BoxScoreDefensiveV2, LeagueLeaders, PlayByPlayV3, BoxScoreAdvancedV3, WinProbabilityPBP
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits
from datetime import datetime, timedelta
from nba_api.stats.endpoints import PlayByPlayV3
import matplotlib.pyplot as plt
import re
from datetime import datetime, timedelta
import seaborn as sns

# Convert PTXXMXX.XXS into seconds
def convert_clock_to_time(clock, quarter):
    # Extract minutes, seconds, and tenths of a second using regular expressions
    match = re.match(r'PT(\d{2})M(\d{2}\.\d{2})S', clock)
    if match:
        minutes, seconds_with_tenths = match.groups()
        # Split seconds and tenths of a second
        seconds, tenths = map(int, seconds_with_tenths.split('.'))
        # Calculate total seconds including tenths
        total_seconds = 720 - (int(minutes) * 60 + seconds) + (quarter - 1) * 720
        return total_seconds
    else:
        return None

# Get play by play data for the game
play = PlayByPlayV3(end_period=0, game_id='0022300383', start_period=0).get_data_frames()[0]

times = []
away_score = []
home_score = []
# difference = []
# everything = []


for index, row in play.iterrows():
    if row['shotResult'] == 'Made' or row['subType'] == 'end':
        times.append(convert_clock_to_time(row['clock'], row['period']))
        away_score.append(int(row['scoreAway']))
        home_score.append(int(row['scoreHome']))
        # difference.append(int(row['scoreHome']) - int(row['scoreAway']))
        # everything.append(row)

times = np.array(times)
# difference = np.array(difference)
away_score = np.array(away_score)
home_score = np.array(home_score)

# print(times)
# print(away_score)
# print(home_score)

score_times = np.array([720, 1440, 2160, 2880])
away_score_intervals = []
home_score_intervals = []

for target in score_times:
    target_values = np.where(times <= target)[-1]
    closest_index = target_values[np.argmin(np.abs(times[target_values] - target))]
    home_score_intervals.append(home_score[closest_index])
    away_score_intervals.append(away_score[closest_index])

    # print(everything[closest_index])
    # print(times[closest_index])
    # print(home_score[closest_index])
    # print(away_score[closest_index])

    # closest_value = target_values[np.argmin(np.abs(target_values - target))
away_score_intervals = np.array(away_score_intervals)
home_score_intervals = np.array(home_score_intervals)
# print("hi")
# print(away_score_intervals)

sns.set(style="whitegrid")

plt.rcParams["figure.figsize"] = [7.50, 7.50]
plt.rcParams["figure.autolayout"] = True
plt.rcParams['font.family'] = 'monospace'  # Choose your desired font family

fig = plt.figure()
ax = fig.add_subplot(111)
# ax.plot(times, difference, drawstyle="steps-pre")
# ax.fill_between(times, difference, where=(difference >=0), step="pre", color='green', alpha=0.3)
# ax.fill_between(times, difference, where=(difference <= 0), step="pre", color='red', alpha=0.3)

# print(len(times))
# print(len(away_score))
# print(len(home_score))

for i in range(len(times)):
    awayScore = away_score[i]
    homeScore = home_score[i]
    timez = times[i]
    # print(awayScore)
    if i > 0 and homeScore > away_score[i-1] and homeScore < awayScore:
        # print("prev")
        # print(f"{home_score[i-1]}:")
        # print(away_score[i-1])
        # print(times[i-1])
        # print("next")
        # print(f"{homeScore}:")
        # print(awayScore)
        # print(timez)
        # print("")
        # print(home_score[i+1])
        # print(away_score[i+1])
        # print(times[i+1])
        # print("")
        time_temp = [times[i-1], times[i]]
        home_score_temp = np.array([home_score[i-1], home_score[i-1]])
        away_score_temp =np.array([away_score[i-1], away_score[i-1]])

        # print(time_temp)
        # print(home_score_temp)
        # print(away_score_temp)

        ax.fill_between(time_temp, away_score_temp, home_score_temp, where=(
    away_score_temp <= home_score_temp), step='post', color='blue', alpha=0.3)
    if i > 0 and awayScore > home_score[i-1] and homeScore > awayScore:
        # print(f"{home_score[i-1]}:")
        # print(away_score[i-1])
        # print("kmcdsklmc")
        # print(f"{homeScore}:")
        # print(awayScore)

        time_temp = [times[i-1], times[i]]
        home_score_temp = np.array([home_score[i-1], home_score[i-1]])
        away_score_temp =np.array([away_score[i-1], away_score[i-1]])

        # print(time_temp)
        # print(home_score_temp)
        # print(away_score_temp)

        ax.fill_between(time_temp, away_score_temp, home_score_temp, where=(
    away_score_temp >= home_score_temp), step='post', color='orange', alpha=0.3)


ax.plot(times, away_score, drawstyle="steps-post", label="Kings")
ax.plot(times, home_score, drawstyle="steps-post", label="Grizzlies")

ax.fill_between(times, home_score, away_score, where=(home_score <= away_score), step='post', color='green', alpha=0.3)
ax.fill_between(times, home_score, away_score, where=(home_score >= away_score), step='post', color='red', alpha=0.3)

plt.xlim([0, max(times) + 60])
if away_score[-1] > home_score[-1]:
    plt.ylim([0, away_score[-1] + 5])
else:
    plt.ylim([0, home_score[-1] + 5])


# ax.tick_params(axis='y', direction='out', length=6, width=2, colors='black', grid_alpha=0.5)
ax.yaxis.grid(True, linestyle='--', linewidth=1)

# Plot points for each quarter
ax.scatter(score_times, away_score_intervals, color='red', zorder=5, alpha=0.75)
ax.scatter(score_times, home_score_intervals, color='red', zorder=5, alpha=0.75)

# Create annotations for each labeled point
for i in range(len(score_times)):
    if away_score_intervals[i] >= home_score_intervals[i]:
        away_score_coor = (-5, 7.5)
        away_score_ha = 'right'
        home_score_coor = (4, -13) 
        home_score_ha = 'left'
    else:
        away_score_coor = (4, -13)
        away_score_ha = 'left'
        home_score_coor = (-5, 7.5) 
        home_score_ha = 'right'
    
    ax.annotate(f'NYK:{str(away_score_intervals[i])}', (score_times[i], away_score_intervals[i]), textcoords="offset points", xytext=away_score_coor, ha=away_score_ha, fontsize=8)
    ax.annotate(f'SAS:{str(home_score_intervals[i])}', (score_times[i], home_score_intervals[i]), textcoords="offset points", xytext=home_score_coor, ha=home_score_ha, fontsize=8, color='red')


plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
sns.despine(left=True)
sns.despine(bottom=True)


plt.title('Grizzlies v. Kings')

# Custom x-ticks for each quarter
custom_xticks = [720, 1440, 2160, 2880]
custom_labels = ['EO-Q1', 'EO-Q2', 'EO-Q3', 'EO-Q4']
ax.set_xticks(custom_xticks)
ax.set_xticklabels(custom_labels)

# Add legend
plt.legend()

# plt.savefig('your_graph.png', format='png')


# Show the plot
plt.show()



# Use step to create a staircase plot with filled areas
# ax.step(times, home_score, label='Home Team', where='post', linewidth=2)
# ax.step(times, away_score, label='Away Team', where='post', linewidth=2)
# ax.step(times, difference, label='Lead Tracker', drawstyle="steps", linewidth=2)


# plt.fill_between(times, difference, y2, where=(difference >= y2), step='pre', interpolate=True, color='green', alpha=0.3, label='Fill between y=0 and y1')
# plt.fill_between(times, difference, y2, where=(difference <= y2), step='pre', interpolate=True, color='red', alpha=0.3, label='Fill between y=0 and y1')

# plt.plot(times, difference, drawstyle="steps-pre")

# plt.plot(times, home_score, drawstyle="steps-pre")
# plt.plot(times, away_score, drawstyle="steps-pre")

# plt.fill_between(times, home_score, away_score, where=(home_score >= away_score), step='pre', interpolate=True, color='green', alpha=0.3, label='Fill between y=0 and y1')
# plt.fill_between(times, away_score, home_score, where=(home_score <= away_score), step='pre', interpolate=True, color='red', alpha=0.3, label='Fill between y=0 and y1')


# plt.fill_between(time, difference, y2, where=(y1 >= y2), interpolate=True, color='green', alpha=0.3, label='Fill between y=0 and y1')


# ax.fill_between(time, home_score, home_score, color='gray', alpha=0.3, label='Shaded Area')

# # Fill between the steps
# ax.fill_between(times, home_score, step='post', alpha=0.5)
# ax.fill_between(times, away_score, step='post', alpha=0.5)


# plt.step(times, home_score, label='Home Team', where='post')
# plt.step(times, away_score, label='Away Team', where='post')


# plt.xlabel('Time (seconds)')
# plt.ylabel('Score')


# import matplotlib.pyplot as plt
# import numpy as np

# x = np.linspace(0,50,35)
# y = np.random.exponential(1, len(x))
# y2 = np.random.exponential(1, len(x))

# plt.fill_between(x,y, step="pre", alpha=0.4)
# plt.fill_between(x,y2, step="pre", alpha=0.4)

# plt.plot(x,y, drawstyle="steps")
# plt.plot(x,y2, drawstyle="steps")

# plt.show()

# import pandas as pd
# import matplotlib.pyplot as plt

# # Use an example game_id, you'll need to replace this with the game you are interested in
# game_id = '0022300354' # Format: '00221' + game number (last 5 digits)

# # Instantiate the play by play endpoint
# pbp = PlayByPlayV3(game_id=game_id)

# # Get the DataFrame
# pbp_df = pbp.get_data_frames()[0]

# # Filter out rows where 'SCORE' column is NaN as these don't represent scoring plays
# pbp_df = pbp_df[pbp_df['shotResult'] != 'Missed'].dropna()

# # Split the 'SCORE' column into two separate columns for home and visitor scores
# pbp_df[['scoreHome', 'scoreAway']] = pbp_df['SCORE'].str.split(' - ', expand=True)
# pbp_df['scoreHome'] = pd.to_numeric(pbp_df['scoreHome'])
# pbp_df['scoreAway'] = pd.to_numeric(pbp_df['scoreAway'])

# # Convert 'PCTIMESTRING' to a timedelta object and then to seconds
# # This will be used to plot the scores against the game clock
# pbp_df['SECONDS'] = pd.to_timedelta('00:' + pbp_df['PCTIMESTRING']).dt.total_seconds()
# pbp_df['SECONDS_REMAINING'] = (48*60) - (pbp_df['PERIOD']-1)*12*60 - pbp_df['SECONDS']

# # Plot the scores
# plt.figure(figsize=(14, 7))
# plt.plot(pbp_df['SECONDS_REMAINING'], pbp_df['HOME_SCORE'], label='Home Team')
# plt.plot(pbp_df['SECONDS_REMAINING'], pbp_df['VISITOR_SCORE'], label='Visitor Team')

# # Reverse the x-axis to show time elapsing from left to right
# plt.gca().invert_xaxis()

# plt.xlabel('Time Remaining (seconds)')
# plt.ylabel('Score')
# plt.title(f'Score Over Time for Game ID {game_id}')
# plt.legend()
# plt.show()


# for i in range(len(play)):
#     if play.loc['isFieldGoal'] == 1:
#         print(play.iloc[i])

# play = BoxScoreAdvancedV3(end_period=0, game_id='0022300104', start_period=0).get_data_frames()[0]

# for i in range(len(play)):
#     print(play.iloc[i])

# play = WinProbabilityPBP(game_id='0022300354').get_data_frames()[0]

# for i in range(len(play)):
#     p = play.iloc[i]
#     if p['DESCRIPTION'] and p['HOME_PCT']:
#         print(p)


# import matplotlib.pyplot as plt
# import seaborn as sns
# from nba_api.stats.endpoints import shotchartdetail

# def get_shot_data(game_id):
#     shot_chart = shotchartdetail.ShotChartDetail(
#         team_id=0,
#         player_id=0,
#         game_id_nullable=game_id,
#         context_measure_simple='FGA'
#     )
#     shot_data = shot_chart.get_data_frames()[0]
#     return shot_data

# def create_heatmap(shot_data):
#     plt.figure(figsize=(12, 11))
#     sns.kdeplot(
#         x=shot_data.LOC_X,
#         y=shot_data.LOC_Y,
#         cmap='YlOrRd',
#         fill=True,  # Use fill instead of shade
#         thresh=0,   # Adjust this value as needed
#     )
#     plt.xlim(-300, 300)
#     plt.ylim(0, 564)
#     plt.title('NBA Game Shot Chart Heatmap')
#     plt.show()

# def main():
#     # Replace '0022000001' with the desired NBA game ID
#     game_id = '0022300280'

#     shot_data = get_shot_data(game_id)
#     create_heatmap(shot_data)

# if __name__ == "__main__":
#     main()


# field_goals = [row for index,
#                row in plays.iterrows()]

# for index, row in plays.iterrows():
#     print(row["personId"])


# print(field_goals)


# page_elements = slide.get('pageElements')


# from nba_api.stats.static import players

# from nba_api.stats.endpoints import shotchartdetail
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd
# from matplotlib.patches import Circle

# # Specify the player and team
# player_id = 201939  # Stephen Curry's player ID
# team_id = 1610612744  # Golden State Warriors' team ID

# # Fetch shot chart data
# shot_chart = shotchartdetail.ShotChartDetail(
#     player_id=player_id,
#     team_id=team_id,
#     season_type_all_star='Regular Season',
#     context_measure_simple='FGA'
# )
# shot_data = shot_chart.get_data_frames()[0]


# def draw_court():
#     # Draw court lines
#     plt.plot([-250, 250], [0, 0], color='black')  # Baseline
#     plt.plot([-250, 250], [500, 500], color='black')  # Baseline
#     plt.plot([-250, -250], [0, 500], color='black')  # Left sideline
#     plt.plot([250, 250], [0, 500], color='black')  # Right sideline
#     plt.plot([-250, 250], [250, 250], color='black')  # Center line

#     # Draw three-point line
#     plt.plot([-220, -220], [0, 140], color='black')
#     plt.plot([220, 220], [0, 140], color='black')
#     plt.plot([-220, -250], [140, 140], color='black')
#     plt.plot([220, 250], [140, 140], color='black')
#     plt.plot([0, 0], [140, 500], color='black')

#     # Draw free-throw circle
#     circle = plt.Circle((0, 250), 60, fill=False, color='black')
#     plt.gca().add_patch(circle)

#     # Add labels
#     plt.text(0, 470, 'NBA', ha='center',
#              va='center', fontsize=10, color='black')
#     plt.text(0, 480, '3-Point Line', ha='center',
#              va='center', fontsize=10, color='black')


# # Set up the plot
# plt.figure(figsize=(12, 11))
# plt.scatter(shot_data.LOC_X, shot_data.LOC_Y,
#             c=shot_data.SHOT_MADE_FLAG, cmap='bwr', s=30, alpha=0.6)

# # Customize plot
# plt.title(f"Curry Shot Chart")
# plt.gca().set_aspect('equal', adjustable='box')
# plt.xlim(-250, 250)
# plt.ylim(0, 500)

# # Draw court lines and add labels
# draw_court()
# plt.show()


# # Define the parameters for the API request
# params = {
#     'player_id': player_id,  # Corrected parameter name
#     'team_id': team_id,
#     'season_type_all_star': 'Regular Season',
#     'context_measure_simple': 'FGA',
#     'last_n_games': 0,
#     'league_id': '00',
# }

# # Make the API request
# shot_data = shotchartdetail.ShotChartDetail(**params)
# shot_chart = shot_data.get_data_frames()[0]

# # Plot the shot chart
# plt.figure(figsize=(12, 11))
# plt.scatter(shot_chart['LOC_X'], shot_chart['LOC_Y'],
#             c='blue', marker='o', s=50, alpha=0.5)
# plt.title('Stephen Curry Shot Chart (2022-2023 Season)')
# plt.xlabel('X - Distance from the basket (feet)')
# plt.ylabel('Y - Distance from the baseline (feet)')
# plt.xlim(-250, 250)
# plt.ylim(-47.5, 422.5)
# plt.show()


# import requests
# import matplotlib.pyplot as plt
# from matplotlib.patches import Circle, Rectangle, Arc
# from nba_api.stats.endpoints import ShotChartDetail


# def draw_court(ax=None, color='black', lw=2, outer_lines=False):
#     # If an axes object isn't provided to plot onto, just get the current one
#     if ax is None:
#         ax = plt.gca()

#     # Create the various parts of an NBA basketball court

#     # Create the hoop
#     hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

#     # Create backboard
#     backboard = Rectangle((-30, -7.5), 60, 0, linewidth=lw, color=color)

#     # The paint
#     # Create the outer box 0f the paint, width=16ft, height=19ft
#     outer_box = Rectangle((-80, -47.5), 160, 190,
#                           linewidth=lw, color=color, fill=False)
#     # Create the inner box of the paint, widt=12ft, height=19ft
#     inner_box = Rectangle((-60, -47.5), 120, 190,
#                           linewidth=lw, color=color, fill=False)

#     # Create free-throw line
#     free_throw_circle = Circle(
#         (0, 142.5), radius=15, linewidth=lw, color=color, fill=False)
#     free_throw_circle_arc = Arc(
#         (0, 142.5), 15, 15, theta1=0, theta2=180, linewidth=lw, color=color)

#     # Restricted Zone, it is an arc with 4ft radius from center of the hoop
#     restricted_area = Arc((0, 0), 80, 80, theta1=0,
#                           theta2=180, linewidth=lw, color=color)

#     # Three-point line
#     # Create the side 3pt lines, they are 22ft away from the hoop
#     corner_three_a = Rectangle(
#         (-220, -47.5), 0, 140, linewidth=lw, color=color)
#     corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
#     # Create the 3pt arc - center of arc will be the hoop, arc is 23.75 ft away from hoop
#     three_arc = Arc((0, 0), 475, 475, theta1=22,
#                     theta2=158, linewidth=lw, color=color)

#     # Center Court
#     center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180,
#                            theta2=0, linewidth=lw, color=color)
#     center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180,
#                            theta2=0, linewidth=lw, color=color)

#     # List of the court elements to be plotted onto the axes
#     court_elements = [hoop, backboard, outer_box, inner_box, free_throw_circle, free_throw_circle_arc,
#                       restricted_area, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

#     # Draw the court elements onto the axes
#     for element in court_elements:
#         ax.add_patch(element)

#     return ax


# def plot_shot_chart(player_id, season, game_id, team_id):
#     # Get shot chart data using NBA API
#     shot_chart_detail = ShotChartDetail(
#         player_id=player_id, season=season, game_id=game_id, team_id=team_id)
#     shot_data = shot_chart_detail.get_data_frames()[0]

#     # Set up the plot
#     fig, ax = plt.subplots(figsize=(12, 11))
#     draw_court(ax)
#     plt.xlim(-250, 250)
#     plt.ylim(422.5, -47.5)

#     # Plot the shots
#     plt.scatter(shot_data['LOC_X'], shot_data['LOC_Y'],
#                 c='green', s=10, alpha=0.6)

#     # Display the plot
#     plt.show()


# # Example usage
# player_id = 201939  # Stephen Curry's player ID
# season = '2022-23'
# game_id = '0022200010'  # Replace with the actual game ID
# team_id = None  # Set to None to get all teams
# plot_shot_chart(player_id, season, game_id, team_id)


# # Filter out plays that are not field goals
# field_goals = [play for play in plays if play['EVENTMSGTYPE'] == 1]

# # Sort field goals by score margin (descending order)
# sorted_field_goals = sorted(
#     field_goals, key=lambda x: x['score_margin'], reverse=True)

# # Get the top 5 plays
# top_5_plays = sorted_field_goals[:5]

# # Print or process the top 5 plays
# for i, play in enumerate(top_5_plays, start=1):
#     print(
#         f"Top Play {i}: {play['HOMEDESCRIPTION']} vs {play['VISITORDESCRIPTION']}")


# my_string_without_spaces = my_string.replace(' ', '')
# print(my_string_without_spaces)


# # Specify the season and the team's ID (e.g., the ID for the Los Angeles Lakers is 1610612747)
# season = '23-24'  # Replace this with the desired season
# team_id = 1610612739  # Replace this with the desired team's ID

# # Retrieve the team dashboard by general splits
# team_info = TeamDashboardByGeneralSplits(team_id=team_id)
# team_info_df = team_info.get_data_frames()[0]
# print(team_info_df)

# # Extract the win-loss record
# wins = team_info_df['W']
# losses = team_info_df['L']

# # Print the win-loss record
# print(f"Team {team_id} has {wins.iloc[0]} wins and {losses.iloc[0]} losses in the {season} season.")

# from nba_api.stats.endpoints import teamyearbyyearstats

# # Specify the team's ID (e.g., the ID for the Los Angeles Lakers is 1610612747)
# team_id = 1610612739  # Replace this with the desired team's ID

# # Retrieve the team's year-by-year statistics
# team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
# team_stats_df = team_stats.get_data_frames()[0].iloc[-1]

# # Display the team's statistics for the entire current season
# print(team_stats_df["WINS"])


# from tqdm import tqdm
# import time

# # Your iterable (e.g., range, list, etc.)
# iterable = range(100)

# GREEN = "\033[92m"

# RESET_COLOR = "\033[0m"

# # Wrap the iterable with tqdm
# for item in tqdm(iterable, bar_format=f"{{l_bar}}{GREEN}{{bar}}{RESET_COLOR}{{r_bar}}", desc="Processing items", unit="item", total=len(iterable), leave=True):
#     # Your processing logic here
#     time.sleep(0.1)  # Simulating some work


# from nba_api.stats.endpoints import playerdashboardbylastngames

# # Define the parameters
# player_id = 201939  # Example player ID for Stephen Curry
# last_n_games = 10  # Number of games to consider

# # Retrieve the player's dashboard by the last 'n' games
# player_info = playerdashboardbylastngames.PlayerDashboardByLastNGames(player_id=player_id, last_n_games=last_n_games)
# player_info_df = player_info.get_data_frames()[0]

# # Display the player rankings based on the last 'n' games
# print(player_info_df)


# from nba_api.stats.endpoints import playerdashboardbyyearoveryear

# # Specify the player's ID (e.g., the ID for Stephen Curry is 201939)
# player_id = 201939  # Replace this with the desired player's ID

# # Retrieve the player's statistics for the entire current season
# player_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=player_id)
# player_stats_df = player_stats.get_data_frames()[1]

# # Display the player's statistics for the entire current season
# print("p", player_stats_df)

# game_finder = LeagueGameFinder(date_from_nullable=CONSTANTS.yesterday_date_string,
#                                        date_to_nullable=CONSTANTS.yesterday_date_string,
#                                        league_id_nullable='00').get_data_frames()[0]

# # print(game_finder)

# unique_game_ids = game_finder['GAME_ID'].unique()


# game_id = unique_game_ids[0]


# print(game_id)
# player_id = '1629684'  # Replace with the player's ID you're interested in

# print(teams.get_teams())

# # Get the player's stats for the specified game
# boxscore = BoxScoreDefensiveV2(game_id=game_id).get_data_frames()[1]
# print(boxscore)


# for index, row in boxscore.iterrows():
#     print(row)
#     break

# boxscore = BoxScoreTraditionalV3(game_id=game_id).get_data_frames()[1]
# print(boxscore.iloc[0])

# for index, row in boxscore.iterrows():
#     if(row['minutes']):
#         print(row)
#         break


# game_id = unique_game_ids[0]
# player_id = '1629684'  # Replace with the player's ID you're interested in

# # Get the player's stats for the specified game
# boxscore = BoxScoreTraditionalV3(game_id=game_id)
# player_stats = boxscore.get_data_frames()[0]  # This will contain player-specific stats
# print(player_stats.iloc[17])

# if (player_stats.iloc[17]['minutes'] == 0):
#     print("none")
# else:
#     print("ewknwek")


# # Print or process the player's stats as needed
# # print(player_stats)

# print("hi")


# graph_url = 'https://graph.facebook.com/v17.0/'
# def post_image():
#     caption='jekndlkend'
#     image_url='https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png'
#     instagram_account_id=CONSTANTS.business_id
#     access_token=CONSTANTS.INSTAGRAM_ACCESS_TOKEN
#     url = graph_url + instagram_account_id + '/media'
#     param = dict()
#     param['access_token'] = access_token
#     param['caption'] = caption
#     param['image_url'] = image_url
#     response = requests.post(url, params=param)
#     response = response.json()
#     return response

# hi = post_image()
# print(hi)

# graph_url = 'https://graph.facebook.com/v17.0/'
# # creation_id is container_id
# def publish_container(creation_id = hi,instagram_account_id=CONSTANTS.business_id,access_token=CONSTANTS.INSTAGRAM_ACCESS_TOKEN):
#     url = graph_url + instagram_account_id + '/media_publish'
#     param = dict()
#     param['access_token'] = access_token
#     param['creation_id'] = creation_id
#     response = requests.post(url,params=param)
#     response = response.json()
#     return response

# publish_container()


# yesterday_date_string = '03/25/2023'


# from datetime import datetime, timedelta

# current_date = datetime.now()   # Get the current date and time
# current_date_string = current_date.strftime('%Y-%m-%d')    # Format the current date as a string

# yesterday_date = current_date - timedelta(days=1)   # Calculate yesterday's date
# yesterday_date_string = yesterday_date.strftime('%Y-%m-%d')    # Format yesterday's date as a string

# yesterday_date_string = '01/24/2023'

# parsed_date = datetime.strptime(yesterday_date_string, '%m/%d/%y')

# formatted_date = parsed_date.strftime('%B %d, %Y')

#     # Get the day suffix (st, nd, rd, or th)
# day_suffix = 'th' if 11 <= parsed_date.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(parsed_date.day % 10, 'th')

#     # Combine the formatted date and day suffix
# final_formatted_date = formatted_date.replace(' ', f' {parsed_date.day}{day_suffix} ')

# print(final_formatted_date)


# media_path = "downloaded_image.jpg"
# media = CONSTANTS.twitter.media_upload(filename=media_path)
# media_id = media.media_id

# CONSTANTS.client.create_tweet(text="Tweet text", media_ids=[media_id])

# def divide_post(message):
#     if len(message) > 278:
#         parts = math.ceil(len(message) / 278)
#         message = re.split('-------------', message)

#         messagelength = math.ceil(len(message) / parts)
#         chunks = [
#             message[i: i + messagelength]
#             for i in range(0, len(message), messagelength)
#         ]
#         message_chunks = []
#         for i, j in enumerate(chunks):
#             message_chunks.append(
#                 f"({i+1}/{len(chunks)}) " + "".join(j).strip())
#         return message_chunks
#     else:
#         return [message]


# message = divide_post()


# try:
#     # Create the LeagueGameFinder endpoint with the desired parameters
#     game_finder = LeagueGameFinder(date_from_nullable=yesterday_date_string, date_to_nullable=yesterday_date_string, league_id_nullable='00', team_id_nullable='1610612748')
# except:
#     print("error")


#     # Retrieve the game data
# games = game_finder.get_data_frames()[0]


# print(games)

# # desired_date = '03/25/2023'

# # # Specify the Game ID for the desired NBA game
# # game_id = '0022201108'  # Replace with the actual Game ID

# # # Create the LeagueGameFinder endpoint with the desired parameters
# # game_finder = LeagueGameFinder(game_id_nullable=game_id, date_from_nullable=desired_date, date_to_nullable=desired_date, league_id_nullable='00')
# # games = game_finder.get_data_frames()[0]

# # print(games)

# # # Get the team abbreviations
# # home_team_abbr = games['HOME_TEAM_ABBREVIATION'].values[0]
# # visitor_team_abbr = games['VISITOR_TEAM_ABBREVIATION'].values[0]

# # # Construct the match name using team abbreviations
# # match_name = f"{home_team_abbr} vs {visitor_team_abbr}"

# # print("Match Name:", match_name)

# from nba_api.stats.endpoints import BoxScoreSummaryV2

# # Specify the Game ID for the desired NBA game
# game_id = '0022201108'  # Replace with the actual Game ID

# # Create the BoxScoreSummaryV2 endpoint with the desired Game ID
# boxscore_summary = BoxScoreSummaryV2(game_id=game_id)

# # Retrieve game summary data
# game_summary = boxscore_summary.get_data_frames()[0]  # Assuming there's only one DataFrame


# # Extract team abbreviations
# home_team_abbr = game_summary['HOME_TEAM_ID'].iloc[0]
# team_stats = game_summary[game_summary['HOME_TEAM_ID'] == home_team_abbr]
# team_won = team_stats['TEAM_WINS_LOSSES'].iloc[0]
# # home_team_abbr = game_summary.at[0, 'TEAM_WINS_LOSSES']
# print(team_won)
# print(game_summary['VISITOR_TEAM_ID'].iloc[0])
# visitor_team_abbr = game_summary['VISITOR_TEAM_ID'].iloc[0]

# # Print game summary data
# print(game_summary)


# # # teamlog = endpoints.TeamGameLog(season='2022', season_type_all_star='Regular Season', team_id= )

# # # # player_dict = players.get_active_players()
# # # # print(player_dict)

# # # bron = [player for player in player_dict if player['full_name'] == 'LeBron James'][0]
# # # print(bron)

# # # print(top_500_avg)

# # # print("hello")

# from nba_api.stats.endpoints import leaguegamefinder
# from nba_api.stats.endpoints import LeagueGameFinder


# from nba_api.stats.endpoints import LeagueGameLog
# from nba_api.stats.endpoints import ScoreboardV2


# # Specify the date for which you want to retrieve game scores
# desired_date = '03/25/2023'  # Replace this with your desired date

# # Create the LeagueGameFinder endpoint with the desired parameters
# game_finder = LeagueGameFinder(date_from_nullable=desired_date, date_to_nullable=desired_date, league_id_nullable='00')

# # Retrieve the game data
# games = game_finder.get_data_frames()[0]  # Assuming there's only one DataFrame

# print(games)

# gamelog = endpoints.PlayerGameLog(player_id="1629650", date_to_nullable=desired_date, date_from_nullable=desired_date)
# bronGame = gamelog.get_data_frames()[0]

# print(bronGame)

# def calculate_performance_rating(points, minutes_played, o_rebounds, d_rebounds,
#                                 fgm, fga, fg3m, fg3a, ftm, fta,
#                                 assists, steals, blocks, turnovers, plus_minus):
#     fg_percentage = fgm / fga if fga != 0 else 0
#     fg3_percentage = fg3m / fg3a if fg3a != 0 else 0
#     ft_percentage = ftm / fta if fta != 0 else 0

#     performance_rating = (
#         points + o_rebounds + d_rebounds +
#         fgm * 2 + fg3m + ftm +
#         assists * 1.5 + steals * 2 + blocks * 2 -
#         turnovers * 1.5 + plus_minus
#     )

#     # Incorporate shooting percentages
#     shooting_percentage_bonus = (fg_percentage*2 + fg3_percentage*3 + ft_percentage) / 6
#     performance_rating *= (1 + shooting_percentage_bonus)

#     return performance_rating

# # Example statistics
# points = 25
# minutes_played = 35
# o_rebounds = 3
# d_rebounds = 7
# fgm = 10
# fga = 18
# fg3m = 3
# fg3a = 6
# ftm = 2
# fta = 3
# assists = 8
# steals = 2
# blocks = 1
# turnovers = 3
# plus_minus = 10

# # Calculate performance rating
# rating = calculate_performance_rating(
#     points, minutes_played, o_rebounds, d_rebounds,
#     fgm, fga, fg3m, fg3a, ftm, fta,
#     assists, steals, blocks, turnovers, plus_minus
# )

# print("Performance Rating:", rating)


# # Specify the date for which you want to retrieve NBA game data
# desired_date = '2019-03-29'

# # Create the LeagueGameFinder endpoint with the desired parameters
# game_finder = leaguegamefinder.LeagueGameFinder(date_from_nullable=desired_date, date_to_nullable=desired_date)

# # Retrieve the game data
# games = game_finder.get_data_frames()  # Assuming there's only one DataFrame

# # Filter out G-League games based on SEASON_ID
# nba_games = games[games['SEASON_ID'].str.contains('-NBA')]

# print(nba_games)

# # Print out the NBA game data
# for index, row in nba_games.iterrows():
#     print(f"Date: {row['GAME_DATE']} | Home Team: {row['TEAM_NAME']} | Away Team: {row['MATCHUP']} | Home Team Score: {row['PTS']} | Away Team Score: {row['PTS']}")


# bob = LeagueGameLog(league_id='00', date_from_nullable=desired_date, date_to_nullable=desired_date)
# bob = bob.get_data_frames()[0]
# print(bob)

# tf = ScoreboardV2(league_id='00', game_date=desired_date)
# tft = tf.get_data_frames()[0]
# print(tft)
# # Print out the game data, including scores
# for index, row in games.iterrows():
#     print(f"Date: {row['GAME_DATE']} | Home Team: {row['TEAM_NAME']} | Away Team: {row['MATCHUP']} | Home Team Score: {row['PTS']} | Away Team Score: {row['PTS']}")
