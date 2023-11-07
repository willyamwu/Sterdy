import math
import re
import sys
import time
import CONSTANTS
from nba_models.nba_player import NBA_Player
from nba_models.nba_team import NBA_Team
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import LeagueGameFinder, BoxScoreTraditionalV3, BoxScoreDefensiveV2
from datetime import datetime, timedelta

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

        player_boxscore = BoxScoreTraditionalV3(game_id=game).get_data_frames()[0]
        team_boxscore = BoxScoreTraditionalV3(game_id=game).get_data_frames()[2]
        print(team_boxscore)

        for index, row in player_boxscore.iterrows():
            if (row['minutes']):
                player = NBA_Player(row)
                player_data.append(player)
            else:
                pass

        for i in range(len(team_boxscore)):
            team = NBA_Team(team_boxscore.iloc[i])
            team_data.append(team)

        player_data = sort_players_by_rating(player_data)[:10]
        master_dict[game]['PLAYERS'] = player_data
        master_dict[game]['TEAMS'] = team_data
        # print("team data:",team_data[0].team_slug,team_data[0].rating, " dkemdkem ", team_data[1].team_city,team_data[1].rating)
        build_text(game)
        print("-------------")


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
        master_dict[game] = {"SCORE": [] }

    for i in range(0, game_finder.shape[0]):     
        id =  game_finder.at[i, 'GAME_ID']
        master_dict[id]['SCORE'].append({game_finder.at[i, 'TEAM_NAME'].rstrip(' '): str(game_finder.at[i, 'PTS'])})


def build_text(game_id):
    team1 = master_dict[game_id]['TEAMS'][0]
    team2 = master_dict[game_id]['TEAMS'][1]
    players = master_dict[game_id]['PLAYERS']

    # Building the tweet text
    twitter_matchup_text = "\U0001F6A8 #NBA Report for " + CONSTANTS.yesterday_date_string + " \U0001F6A8\n\n"

    for item in master_dict[game_id]['SCORE']:
        for key, value in item.items():
            twitter_matchup_text = twitter_matchup_text + key + ": " + value + "\n"

    # matchup_text = matchup_text + master_dict[game_id]['TWITTER_MATCHUP'] + "\n"
    twitter_matchup_text += master_dict[game_id]['PLAYERS'][0].player_of_the_match()

    instagram_caption = twitter_matchup_text

    twitter_matchup_text += "\nOur Top 10 ⬇️"
    
    master_dict[game_id]['TWITTER_MATCHUP'] = twitter_matchup_text

    instagram_caption += "\n\n\n\n\n" + CONSTANTS.instagram_hashtags
    instagram_caption += f"#{team1.team_name.replace(' ', '')} #{team2.team_name.replace(' ', '')} #{team1.team_slug} #{team2.team_slug} #{team1.team_tricode} #{team2.team_tricode} "

    for i in range(10):
        instagram_caption += f"#{players[i].full_name.replace(' ', '').replace('.', '').replace('-', '')} #{players[i].last_name.replace(' ', '').replace('.', '').replace('-', '')} "
    
    print(instagram_caption)

    count  = 0
    slide_matchup_text = ""
    for item in master_dict[game_id]['SCORE']:
        for key, value in item.items():
            slide_matchup_text = slide_matchup_text + key
            if count == 0:
                slide_matchup_text = slide_matchup_text + " @ "
            count += 1

    master_dict[game_id]['SLIDE_MATCHUP'] = slide_matchup_text

    # print(slide_matchup_text)

    









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



# def calculate_performance_rating(row):
#     player = NBA_Player(row)
#     player.set_rating()
#     print(player.rating)
    # min = game_stats.loc[0, 'MIN']
    # fgm = game_stats.loc[0, 'FGM']
    # # fga = game_stats.loc[0, 'FGA']
    # fg_pct = game_stats.loc[0, 'FG_PCT']
    # fg_3_m = game_stats.loc[0, 'FG3M']
    # # fg_3_a = game_stats.loc[0, 'FG3A']
    # fg_3_pct = game_stats.loc[0, 'FG3_PCT']
    # ftm = game_stats.loc[0, 'FTM']
    # # fta = game_stats.loc[0, 'FTA']
    # ft_pct = game_stats.loc[0, 'FT_PCT']
    # reb = game_stats.loc[0, 'REB']
    # ast = game_stats.loc[0, 'AST']
    # stl = game_stats.loc[0, 'STL']
    # blk = game_stats.loc[0, 'BLK']
    # tov = game_stats.loc[0, 'TOV']
    # pts = game_stats.loc[0, 'PTS']
    # plus_minus = game_stats.loc[0, 'PTS']

    # performance_rating = (
    #     pts + reb + ast * 1.5 + 
    #     fgm + fg_3_m * 1.5 + ftm * 0.5 +
    #     stl * 2 + blk * 2 -
    #     tov * 1.5 + 
    #     plus_minus
    # ) 

    # shooting_percentage_bonus = (fg_pct * 2 + fg_3_pct * 3 + ft_pct) / 6
    # performance_rating *= (1 + shooting_percentage_bonus)

    # performance_rating = round(performance_rating, 2)

    # player_data = CommonPlayerInfo(player_id=id).get_data_frames()[0]
    
    # player_stat = {"NAME": player_data.at[0, 'DISPLAY_FIRST_LAST'], "TEAM":  player_data.at[0, 'TEAM_ABBREVIATION'], "RATING": performance_rating, "PTS": pts, "AST": ast, "REB": reb, "STL": stl, "BLK": blk, "DEF": stl + blk, "TOV": tov, "MIN": min}

    # return player_stat