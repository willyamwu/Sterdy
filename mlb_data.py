import statsapi
from datetime import datetime, timedelta
import CONSTANTS

def get_games():
    schedule = statsapi.schedule(date=None, start_date=CONSTANTS.yesterday_date_string, end_date=CONSTANTS.yesterday_date_string, team="", opponent="", sportId=1, game_id=None)
    print(schedule)
    for game in schedule:
        print(game['away_name'].rstrip(' '), ":", game['away_score'])
        print(game['home_name'].rstrip(' '), ":", game['home_score'])

        # print(game, "\n\n\n")
    # print(schedule)

# print(schedule[0])
def get_roster():
    params = {"teamId": "121",
            "date": CONSTANTS.yesterday_date_string}

    roster = statsapi.get(endpoint="team_roster", params=params)['roster']

    for player in roster:

        playerId = player['person']['id']
        # print(playerId)
        print(player['person']['fullName'])
        personParams = {"personId": playerId,
                        "gamePk": "716974"}

        player_stats = statsapi.get(endpoint="person_stats", params=personParams)['stats'][0]['splits']
        calculate_performance_rating(player_stats)
        

def calculate_performance_rating(player_stats):
    for group in player_stats:
            print(group, "\n")
            if group['group'] == "fielding":
                 if not group['stat']:
                    print(group['group'], " is empty")
            elif group['group'] == "pitching":
                 if not group['stat']:
                    print(group['group'], " is empty")
            elif group['group'] == "hitting":
                 if not group['stat']:
                    print(group['group'], " is empty")

# Check if thats how fantasy points are calculated
def calculate_fielding_rating(id, stats):
    caught_stealing_points = stats['caughtStealing'] * 2
    stolen_bases_points = stats['stolenBases'] * 1.5
    assists_points = stats['assists'] * 1
    putouts_points = stats['putOuts'] * 1
    errors_points = stats['errors'] * -2
    chances_points = stats['chances'] * 0.5
    fielding_points = stats['fielding'] * 1
    passed_ball_points = stats['passedBall'] * -1
    pickoffs_points = stats['pickoffs'] * 2

    total_points = (
        caught_stealing_points +
        stolen_bases_points +
        assists_points +
        putouts_points +
        errors_points +
        chances_points +
        fielding_points +
        passed_ball_points +
        pickoffs_points
    )

    return total_points

get_games()
get_roster()
# print(statsapi.get(endpoint="team_roster", params=params))