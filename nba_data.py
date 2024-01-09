# import math
import re
# import sys
# import time
import CONSTANTS
import numpy as np
from nba_models.nba_player import NBA_Player
from nba_models.nba_team import NBA_Team
from nba_api.stats.endpoints import LeagueGameFinder, BoxScoreTraditionalV3, PlayByPlayV3
# from datetime import datetime, timedelta

all_text = {}
master_dict = {}
unique_games = []
game_dict = {}


# Gets all the games that are played on a certain day.
def get_games():
    try:
        game_finder = LeagueGameFinder(date_from_nullable=CONSTANTS.yesterday_date_string,
                                       date_to_nullable=CONSTANTS.yesterday_date_string,
                                       league_id_nullable='00').get_data_frames()[0]

        print(game_finder)
        if game_finder.empty:
            print("No games going on today :(")
            return

    except:
        print("There was an error.")
        return

    unique_game_ids = game_finder['GAME_ID'].unique()
    # print(unique_game_ids)

    get_matchup(game_finder, unique_game_ids)
    # print(game_finder)

    for game in unique_game_ids:
        unique_games.append(game)
        player_data = []
        team_data = []
        # unique_players = get_player_in_game(game)
        # print(unique_players)

        master_dict[game]['DATE'] = CONSTANTS.yesterday_date_string

        player_boxscore = BoxScoreTraditionalV3(
            game_id=game).get_data_frames()[0]
        

        for index, row in player_boxscore.iterrows():
            if (row['minutes']):
                player = NBA_Player(row)
                player_data.append(player)
            else:
                pass

        team_boxscore = BoxScoreTraditionalV3(
            game_id=game).get_data_frames()[2]
                
        for i in range(len(team_boxscore)):
            team = NBA_Team(team_boxscore.iloc[i])
            team_data.append(team)

        play = PlayByPlayV3(end_period=0, game_id=game, start_period=0).get_data_frames()[0]

        play_make_shot_clock = []
        away_score = []
        home_score = []
        # difference = []
        everything = []

        away_team = None
        home_team = None
        count = 0

        for index, row in play.iterrows():
            if row['shotResult'] == 'Made':
                everything.append(row)
                if count > 0:
                    if everything[count]['scoreAway'] > everything[count - 1]['scoreAway']:
                        if team_data[0].team_id == everything[count]['teamId']:
                            home_team = team_data[1]
                            away_team = team_data[0]
                            team_data[0].isHome = False
                            team_data[1].isHome = True
                        else:
                            home_team = team_data[0]
                            away_team = team_data[1]
                            team_data[0].isHome = True
                            team_data[1].isHome = False
                        
                        del everything
                        break
                count += 1


        for index, row in play.iterrows():
            # print(row)
            if row['shotResult'] == 'Made' or row['subType'] == 'end':
                play_make_shot_clock.append(convert_clock_to_time(row['clock'], row['period']))
                away_score.append(int(row['scoreAway']))
                home_score.append(int(row['scoreHome']))
                # difference.append(int(row['scoreHome']) - int(row['scoreAway']))
                # everything.append(row)

        play_make_shot_clock = np.array(play_make_shot_clock)
        # difference = np.array(difference)
        away_score = np.array(away_score)
        home_score = np.array(home_score)


        player_data = sort_players_by_rating(player_data)[:10]
        master_dict[game]['PLAYERS'] = player_data
        master_dict[game]['TEAMS'] = {'HOME': home_team, 'AWAY': away_team, 'SCORE_PROGRESSION': [play_make_shot_clock, home_score, away_score]}



        # master_dict[game]['TEAMS']['BOXSCORE'] = team_data
        # master_dict[game]['TEAMS']['TIMES'] = play_make_shot_clock
        # master_dict[game]['TEAMS']['AWAY_SCORE_PROGRESSION'] = away_score
        # master_dict[game]['TEAMS']['HOME_SCORE_PROGRESSION'] = home_score

        # print(master_dict[game]['TEAMS'][0].team_stats_array)
        # print("team data:",team_data[0].team_slug,team_data[0].rating, " dkemdkem ", team_data[1].team_city,team_data[1].rating)
        build_text(game)
        print("----------------------------------------------")


def sort_players_by_rating(player_data):
    if len(player_data) <= 1:
        return player_data

    pivot = player_data[len(player_data) // 2].rating
    left = [x for x in player_data if x.rating > pivot]
    middle = [x for x in player_data if x.rating == pivot]
    right = [x for x in player_data if x.rating < pivot]

    return sort_players_by_rating(left) + middle + sort_players_by_rating(right)


def get_matchup(game_finder, unique_games):
    for game in unique_games:
        master_dict[game] = {"SCORE": []}

    for i in range(0, game_finder.shape[0]):
        id = game_finder.at[i, 'GAME_ID']
        master_dict[id]['SCORE'].append(
            {game_finder.at[i, 'TEAM_NAME'].rstrip(' '): str(game_finder.at[i, 'PTS'])})


def build_text(game_id):
    count = 0
    slide_matchup_text = ""
    slide_matchup_score_text = ""

    for item in master_dict[game_id]['SCORE']:
        for key, value in item.items():
            slide_matchup_text = slide_matchup_text + key
            slide_matchup_score_text += key + ": " + value
            if count == 0:
                slide_matchup_text = slide_matchup_text + " @ "
                slide_matchup_score_text = key + ": " + value + "    "
            count += 1

    master_dict[game_id]['SLIDE_MATCHUP'] = slide_matchup_text
    master_dict[game_id]['SLIDE_MATCHUP_SCORE'] = slide_matchup_score_text


    team1 = master_dict[game_id]['TEAMS']['HOME']
    team2 = master_dict[game_id]['TEAMS']['AWAY']
    players = master_dict[game_id]['PLAYERS']

    # Building the tweet text
    tweet_text = "\U0001F6A8 #NBA Report for " + \
        CONSTANTS.yesterday_date_string + " \U0001F6A8\n\n"

    instagram_caption = f"{master_dict[game_id]['SLIDE_MATCHUP']} {CONSTANTS.yesterday_date_string}\n\n"


    for item in master_dict[game_id]['SCORE']:
        for key, value in item.items():
            tweet_text = tweet_text + key + ": " + value + "\n"
            instagram_caption = instagram_caption + key + ": " + value + "\n"

    tweet_text += master_dict[game_id]['PLAYERS'][0].player_of_the_match()
    instagram_caption += master_dict[game_id]['PLAYERS'][0].player_of_the_match()

    master_dict[game_id]['TWITTER_MATCHUP'] = tweet_text

    instagram_caption += "\n\n\n\n\n#nba #basketball #bball #🏀 #sterdy "
    instagram_caption += f"#{(team1.team_city + team1.team_name).replace(' ', '')} #{(team2.team_city + team2.team_name).replace(' ', '')} #{team1.team_slug} #{team2.team_slug} #{team1.team_tricode} #{team2.team_tricode} "

    for i in range(1, 10):
        full_name = players[i].full_name.replace(" ", '').replace(
            '.', '').replace('-', '').replace('\'', '')
        # last_name = players[i].last_name.replace(' ', '').replace(
        #     '.', '').replace('-', '').replace('\'', '')
        instagram_caption += f"#{full_name} "

    instagram_caption += "#espn #overtime #BleacherReport #houseofhighlights #jellyfam #ballislife "

    master_dict[game_id]['INSTAGRAM_CAPTION'] = instagram_caption
    print(instagram_caption)

    # print(slide_matchup_text)

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






# def divide_post(message):
#     if len(message) > 279:
#         parts = math.ceil(len(message) / 279)
#         message = re.split('---------------', message)

#         messagelength = math.ceil(len(message) / parts)
#         chunks = [
#             message[i: i + messagelength]
#             for i in range(0, len(message), messagelength)
#         ]
#         message_chunks = []
#         for i, j in enumerate(chunks):
#             if j[0] == "":
#                 print("hi")
#             else:
#                 message_chunks.append(
#                  f"".join(j).strip())
#         return message_chunks
#     else:
#         return [message]

# print(all_text)

# print(master_dict)


# def get_home_team(game_id):
#     boxscore_summary = BoxScoreSummaryV2(game_id=game_id)
#     game_summary = boxscore_summary.get_data_frames()[0]
#     home_team_id = game_summary['HOME_TEAM_ID'].iloc[0]

#     home_team_name = teams.find_team_name_by_id(home_team_id)

#     return home_team_name['full_name'].rstrip(' ') + ": " + str(score_dict[home_team_id])

# def get_visitor_team(game_id):
#     boxscore_summary = BoxScoreSummaryV2(game_id=game_id)
#     game_summary = boxscore_summary.get_data_frames()[0]
#     visitor_team_id = game_summary['VISITOR_TEAM_ID'].iloc[0]

#     visitor_team_name = teams.find_team_name_by_id(visitor_team_id)

#     return visitor_team_name['full_name'].rstrip(' ')  + ": " + str(score_dict[visitor_team_id])

# Posts the tweet in such a way that they are all threaded together
# def post_tweet(message, reply=None):
#     return CONSTANTS.twitter.update_status(status=message, in_reply_to_status_id=reply.id, auto_populate_reply_metadata=True)


# get_data(CONSTANTS.UPDATED_URL)

# text = build_daily_update_text(post_list_array)
# print(text)
# # previous_message = CONSTANTS.twitter.update_status(status=text, auto_populate_reply_metadata=True)
# # for message in all_post_text:
# #     for i in divide_post(message):
# #         print(i)
#         previous_message = post_tweet(i, previous_message)

# # Specify the date for which you want to get game information
# game_date = '2019-03-29'

# # Create a Scoreboard instance
# scoreboard = Scoreboard(game_date=game_date)

# # Get the data from the API
# scoreboard_data = scoreboard.get_data_frames()[0]

# # Now you can work with the data in the scoreboard_data variable
# print(scoreboard_data)


# player_dict = players.get_active_players()
# team = teams.find_teams_by_full_name("Los Angeles Lakers")
# print(team)
# print(player_dict)

# bron = [player for player in player_dict if player['full_name'] == 'LeBron James'][0]
# bron_id = bron['id']
# gamelog = endpoints.PlayerGameLog(player_id=bron_id, season='2022')
# # bronGame = gamelog.get_json()[0]
# # json_string = json.dumps(bronGame, sort_keys=True, indent=4)

# bronGame = gamelog.get_data_frames()[0]
# print(bronGame.iloc[0])
# if isinstance(bronGame, pd.DataFrame):
#     print("Hello")
# bronny = gamelog.get_dict()
# print(json_string)
# print(bronny['resultSets']['name'])

# print(top_500_avg)

# print("hello")

# # find player Ids
# from nba_api.stats.static import players
# player_dict = players.get_players()

# # Use ternary operator or write function
# bron = [player for player in player_dict if player['full_name'] == 'LeBron James'][0]
# bron_id = bron['id']

# # find team Ids
# from nba_api.stats.static import teams
# teams = teams.get_teams()
# GSW = [x for x in teams if x['full_name'] == 'Golden State Warriors'][0]
# GSW_id = GSW['id']

# #game_stats_player
# #could not get DateFrom to work, just use loop with years if necessary
# from nba_api.stats.library.parameters import SeasonAll
# from nba_api.stats.endpoints import playergamelog
# import pandas as pd

# gamelog_bron = playergamelog.PlayerGameLog(player_id='2544', season = '2018')
# df_bron_games_2018 = gamelog_bron.get_data_frames()

# gamelog_bron_all = playergamelog.PlayerGameLog(player_id='2544', season = SeasonAll.all)
# df_bron_games_all = gamelog_bron_all.get_data_frames()

# #find games played by a team or player
# from nba_api.stats.endpoints import leaguegamefinder
# GSW_games = leaguegamefinder.LeagueGameFinder(team_id_nullable=GSW_id).get_data_frames()[0]

# # game play by play data
# from nba_api.stats.endpoints import playbyplay
# pbp = playbyplay.PlayByPlay('0021900429').get_data_frames()[0]

# # Pull data for the top 500 scorers by PTS column
# top_500 = leagueleaders.LeagueLeaders(
#     per_mode48='PerGame',
#     season='2020-21',
#     season_type_all_star='Regular Season',
#     stat_category_abbreviation='PTS'
# ).get_data_frames()[0][:500]

# # Group players by name and player ID and calculate average stats
# top_500_avg = top_500.groupby(['player_name', 'player_id']).mean()[[
#     'min', 'fgm', 'fga', 'ftm', 'fta', 'pts', 'fg3m', 'fg3a', 'gp'
# ]]

