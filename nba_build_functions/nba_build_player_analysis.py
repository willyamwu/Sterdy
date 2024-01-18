import CONSTANTS
from tqdm import tqdm

from nba_build import copy_slide, delete_slide, edit_text_request, edit_image_request, get_images, get_special_keys, get_slide_id
import nba_build

total_tasks = 147
GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

PRESENTATION_ID = '1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw'

player_key_array = ['{T', '{NAME', '{RT', '{P', '{RB',
                    '{A', '{D', '{PM', '{FG', '{FT', '{SH', '{L', '{M', '{S', 
                    '{B', '{FS', '{3F', '{TO', '{PF','{OR', '{DR']

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

        slide_ids = get_slide_id(PRESENTATION_COPY_ID)

        for i in range(3):
            slide_requests = edit_image_request(
                requests=slide_requests, slide=slide_ids[i], image_url=f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{master_dict[game]['PLAYERS'][i].person_id}.png", image_id="MyImage_" + str(i))

        progress_bar.set_description(f"{game_number} Updating Matchup text")
        slide_requests = edit_text_request(slide_requests, '{MATCH}', master_dict[game]['SLIDE_MATCHUP_SCORE'])
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Updating Date text")
        slide_requests = edit_text_request(slide_requests, '{DATE}', CONSTANTS.yesterday_date_string)
        progress_bar.update(1)

        slide_requests = get_special_keys(value=master_dict[game]["PLAYERS"],
                                          progress_bar=progress_bar, game_number=game_number, requests=slide_requests, key_array=player_key_array, iterations=10)
        

        slides_service.presentations().batchUpdate(
            presentationId=PRESENTATION_COPY_ID, body={'requests': slide_requests}).execute()
        
        progress_bar.set_description(f"{game_number} Downloading Images")
        get_images(PRESENTATION_COPY_ID, game_count)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Deleting Slides")
        delete_slide(PRESENTATION_COPY_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} COMPLETE")
        progress_bar.close()