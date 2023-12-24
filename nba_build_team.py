import json
from logging import Logger
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io
import requests
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import CONSTANTS
from PIL import Image
from io import BytesIO
import time
from tqdm import tqdm

from nba_build import copy_slide, delete_slide, edit_text_request, get_images, get_special_keys

total_tasks = 147
GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

PRESENTATION_ID = '1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw'

team_key_array = ['{TEAM', '{W-L', '{TP', '{TRT',
                  '{TFG', '{TA', '{TRB', '{TBL', '{TST', '{TTV', '{TSH']

def create_team_request(drive_service, slides_service, master_dict, game_ids):
    total_games = len(game_ids)

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

        slide_requests = get_special_keys(value=master_dict[game]["TEAMS"],
                                    progress_bar=progress_bar, game_number=game_number, requests=slide_requests, key_array=team_key_array, iterations=2)
        
        slides_service.presentations().batchUpdate(
            presentationId=PRESENTATION_COPY_ID, body={'requests': slide_requests}).execute()
        
        progress_bar.set_description(f"{game_number} Downloading Images")
        get_images(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Deleting Slides")
        delete_slide(PRESENTATION_COPY_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} COMPLETE")
        progress_bar.close()



