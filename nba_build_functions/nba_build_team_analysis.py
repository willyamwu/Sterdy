import json
from logging import Logger
from pty import master_open
import re
import CONSTANTS
from PIL import Image
from io import BytesIO
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from nba_api.stats.endpoints import PlayByPlayV3

from nba_build import copy_slide, delete_slide, edit_text_request, get_images, get_special_keys
import nba_build

total_tasks = 147
GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

PRESENTATION_ID = '1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw'

team_key_array = ['{TEAM', '{W-L', '{TP', '{TRT',
                  '{TFG', '{TA', '{TRB', '{TBL', '{TST', '{TTV', '{TSH']

def create_team_request(master_dict, game_ids):
    total_games = len(game_ids)
    slides_service = nba_build.slides_service

    for game_count, game in enumerate(game_ids, start=1):
        slide_requests = []
        game_number = f"Game {str(game_count)}/{total_games}"
        progress_bar = tqdm(total=total_tasks, bar_format=f"{{l_bar}}{GREEN}{{bar}}{RESET_COLOR}{{r_bar}}", desc=game_number, unit="task")

        progress_bar.set_description(f"{game_number} Creating a Copy of the Slide")
        PRESENTATION_COPY_ID = copy_slide(PRESENTATION_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Updating Matchup text")
        slide_requests = edit_text_request(slide_requests, '{MATCH}', master_dict[game]['SLIDE_MATCHUP'])
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Updating Date text")
        slide_requests = edit_text_request(slide_requests, '{DATE}', CONSTANTS.yesterday_date_string)
        progress_bar.update(1)

        slide_requests = get_special_keys(value=[master_dict[game]["TEAMS"]['HOME'], master_dict[game]["TEAMS"]['AWAY']],
                                    progress_bar=progress_bar, game_number=game_number, requests=slide_requests, key_array=team_key_array, iterations=2)
        
        slides_service.presentations().batchUpdate(
            presentationId=PRESENTATION_COPY_ID, body={'requests': slide_requests}).execute()
        
        progress_bar.set_description(f"{game_number} Downloading Images")
        get_images(PRESENTATION_COPY_ID, game_count)
        progress_bar.update(1)

        generate_point_graph(master_dict[game]['TEAMS'])

        progress_bar.set_description(f"{game_number} Deleting Slides")
        delete_slide(PRESENTATION_COPY_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} COMPLETE")
        progress_bar.close()

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

def generate_point_graph(dict_data):
    # if dict_data['BOXSCORE'][0].isHome:
    #     home_team_index = 0
    #     away_team_index = 1
    # else:
    #     home_team_index = 1
    #     away_team_index = 0


    # home_team_name = dict_data['BOXSCORE'][0].tri if dict_data['BOXSCORE'][0]
    # away_team = if dict_data[]
    # # Get play by play data for the game
    # play = PlayByPlayV3(end_period=0, game_id='0022300383', start_period=0).get_data_frames()[0]

    # play_make_shot_clock = []
    # away_score = []
    # home_score = []
    # # difference = []
    # # everything = []


    # for index, row in play.iterrows():
    #     if row['shotResult'] == 'Made' or row['subType'] == 'end':
    #         play_make_shot_clock.append(convert_clock_to_time(row['clock'], row['period']))
    #         away_score.append(int(row['scoreAway']))
    #         home_score.append(int(row['scoreHome']))
    #         # difference.append(int(row['scoreHome']) - int(row['scoreAway']))
    #         # everything.append(row)

    play_make_shot_clock = dict_data['SCORE_PROGRESSION'][0]
    # difference = np.array(difference)
    home_score = dict_data['SCORE_PROGRESSION'][1]
    away_score = dict_data['SCORE_PROGRESSION'][2]

    print(play_make_shot_clock)
    print(home_score)
    print(away_score)

    # score_times = np.array([720, 1440, 2160, 2880])
    # away_score_intervals = []
    # home_score_intervals = []

    # for target in score_times:
    #     target_values = np.where(play_make_shot_clock <= target)[-1]
    #     closest_index = target_values[np.argmin(np.abs(play_make_shot_clock[target_values] - target))]
    #     home_score_intervals.append(home_score[closest_index])
    #     away_score_intervals.append(away_score[closest_index])

    #     # print(everything[closest_index])
    #     # print(times[closest_index])
    #     # print(home_score[closest_index])
    #     # print(away_score[closest_index])

    #     # closest_value = target_values[np.argmin(np.abs(target_values - target))
    # away_score_intervals = np.array(away_score_intervals)
    # home_score_intervals = np.array(home_score_intervals)
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

    ax.plot(play_make_shot_clock, home_score, drawstyle="steps-post", color='red', label="Grizzlies")
    ax.plot(play_make_shot_clock, away_score, drawstyle="steps-post", color='blue', label="Kings")

    for i in range(len(play_make_shot_clock)):
        awayScore = away_score[i]
        homeScore = home_score[i]
        timez = play_make_shot_clock[i]
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
            time_temp = [play_make_shot_clock[i-1], play_make_shot_clock[i]]
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

            time_temp = [play_make_shot_clock[i-1], play_make_shot_clock[i]]
            home_score_temp = np.array([home_score[i-1], home_score[i-1]])
            away_score_temp =np.array([away_score[i-1], away_score[i-1]])

            # print(time_temp)
            # print(home_score_temp)
            # print(away_score_temp)

            ax.fill_between(time_temp, away_score_temp, home_score_temp, where=(
        away_score_temp >= home_score_temp), step='post', color='red', alpha=0.3)
            


    ax.fill_between(play_make_shot_clock, home_score, away_score, where=(home_score <= away_score), step='post', color='blue', alpha=0.3)
    ax.fill_between(play_make_shot_clock, home_score, away_score, where=(home_score >= away_score), step='post', color='red', alpha=0.3)

    plt.xlim([0, max(play_make_shot_clock) + 60])
    if away_score[-1] > home_score[-1]:
        plt.ylim([0, away_score[-1] + 5])
    else:
        plt.ylim([0, home_score[-1] + 5])


    # ax.tick_params(axis='y', direction='out', length=6, width=2, colors='black', grid_alpha=0.5)
    ax.yaxis.grid(True, linestyle='--', linewidth=1)


    score_times = np.array([720, 1440, 2160, 2880])
    home_score_intervals = []
    away_score_intervals = []
    for score_time in score_times:
        index = np.argmax(play_make_shot_clock == score_time)
        home_score_intervals.append(home_score[index])
        away_score_intervals.append(away_score[index])

    print(home_score_intervals)
    print(away_score_intervals)

    home_score_intervals = np.array(home_score_intervals)
    away_score_intervals = np.array(away_score_intervals)

    print(home_score_intervals)
    print(away_score_intervals)

    # Plot points for each quarter
    ax.scatter(score_times, home_score_intervals, color='blue', zorder=5, alpha=0.75)
    ax.scatter(score_times, away_score_intervals, color='red', zorder=5, alpha=0.75)

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

        ax.annotate(f':{str(home_score_intervals[i])}', (score_times[i], home_score_intervals[i]), textcoords="offset points", xytext=home_score_coor, ha=home_score_ha, fontsize=8)
        ax.annotate(f'HI:{str(away_score_intervals[i])}', (score_times[i], away_score_intervals[i]), textcoords="offset points", xytext=away_score_coor, ha=away_score_ha, fontsize=8)


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

    plt.savefig('my_plot.jpeg')




