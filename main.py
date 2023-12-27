import nba_data
import nba_build
import nba_post
import CONSTANTS
from nba_build_functions import nba_build_team_analysis

start_up_prompt = '''(1) Daily Game Analysis
(2) Player Rankings 
(3) Team Rankings'''


def main():
    print("Target Date:", CONSTANTS.yesterday_date_string)
    # Uncomment in event of multiple functions added

    print(start_up_prompt)
    path_finder()


# Choose your own adventure
def path_finder():
    while (True):
        user_input = input("Choose a command: ")
        if user_input == "1":
            print("Daily Game Analysis -- SELECTED")
            # Activate nba scripts
            nba_data.get_games()
            # print(nba_data.master_dict)
            # nba_build.intialize(nba_data.master_dict, nba_data.unique_games)
            nba_build.create_request(
                nba_data.master_dict, nba_data.unique_games)
            # nba_build_team_analysis.create_team_request(nba_data.master_dict, nba_data.unique_games)
            nba_post.twitter_post(nba_build.all_image_paths,
                                  nba_data.master_dict, nba_data.unique_games)
            # nba_build.remove_all_photos(nba_build.all_image_paths)
            print("OPERATION COMPLETE")
            break
        elif user_input == "2":
            print("Player Rankings -- SELECTED")
            break
        elif user_input == "3":
            print("Team Rankings -- SELECTED")
            break
        else:
            print("INVALID INPUT")


if __name__ == "__main__":
    main()
