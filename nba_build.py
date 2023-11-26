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

CLIENT_FILE = 'client_secret.json'
CLIENT_ID = CONSTANTS.GOOGLE_CLIENT_ID
CLIENT_SECRET = CONSTANTS.GOOGLE_CLIENT_SECRET
PRESENTATION_ID = '1OkCzw0NV6ikJItZn2uU4Fxsd5ae2mDR31FLVkezsk7o'

player_key_array = ['{T', '{NAME', '{RT', '{P', '{RB',
                    '{A', '{D', '{PM', '{FG', '{FT', '{SH', '{L']
team_key_array = ['{TEAM', '{W-L', '{TP', '{TRT',
                  '{TFG', '{TA', '{TRB', '{TBL', '{TST', '{TTV', '{TSH']

SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations',
)

game_count = 1
all_image_paths = {}

# Creating credentials
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Building the services
slides_service = build('slides', 'v1', credentials=creds)
dir(slides_service)

drive_service = build('drive', 'v3', credentials=creds)
dir(drive_service)

total_tasks = 147
GREEN = "\033[92m"
RESET_COLOR = "\033[0m"


# # page_elements = slide.get('pageElements')

# # def get_slide_id(id):
# presentation = slides_service.presentations().get(
#     presentationId=PRESENTATION_ID).execute()

# slides_data = presentation.get('slides', [])
# slide_ids = []
# for slide in slides_data:
#     slide_id = slide['objectId']
#     slide_ids.append(slide_id)

# slide = slide_ids[2]
# print(slide)


# IMAGE_URL = (
#     "https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg"
# )

# print("hi")
# # The image URL.
# IMAGE_URL = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/203507.png'


# requests = []
# image_id = "MyImage_11"
# emu4M = {"magnitude": 4000000, "unit": "EMU"}
# requests.append(
#     {
#         "createImage": {
#             "objectId": image_id,
#             "url": IMAGE_URL,
#             "elementProperties": {
#                 "pageObjectId": slide,
#                 "size": {"height": emu4M, "width": emu4M},
#                 "transform": {
#                     "scaleX": 1.5,
#                     "scaleY": 1.5,
#                     "translateX": 3620064,
#                     "translateY": 2056656,
#                     "unit": "EMU",
#                 },
#             },
#         }
#     }
# )

# # Execute the request.
# body = {"requests": requests}
# response = (
#     slides_service.presentations()
#     .batchUpdate(presentationId=PRESENTATION_ID, body=body)
#     .execute()
# )
# create_image_response = response.get("replies")[0].get("createImage")
# print(f"Created image with ID: {(create_image_response.get('objectId'))}")


# quit()


def create_request(master_dict, game_ids, game_dict):

    game_count = 1
    total_games = len(game_ids)

    for game in game_ids:
        slide_requests = []
        game_number = f"Game {str(game_count)}/{total_games}"
        progress_bar = tqdm(
            total=total_tasks, bar_format=f"{{l_bar}}{GREEN}{{bar}}{RESET_COLOR}{{r_bar}}", desc=game_number, unit="task")

        progress_bar.set_description(
            f"{game_number} Creating a Copy of the Slide")
        PRESENTATION_COPY_ID = copy_slide()
        progress_bar.update(1)

        slide_ids = get_slide_id(PRESENTATION_ID)

        for i in range(3):
            slide_requests = edit_image_request(
                requests=slide_requests, slide=slide_ids[i], image_url=f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{master_dict[game]['PLAYERS'][i].person_id}.png", image_id="MyImage_" + str(i))

        progress_bar.set_description(f"{game_number} Updating Date text")
        slide_requests = edit_text_request(slide_requests, '{MATCH}',
                                           master_dict[game]['SLIDE_MATCHUP'])
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Updating Matchup text")
        slide_requests = edit_text_request(
            slide_requests, '{DATE}', CONSTANTS.yesterday_date_string)

        progress_bar.update(1)

        slide_requests = get_special_keys(value=master_dict[game]["TEAMS"],
                                          progress_bar=progress_bar, game_number=game_number, requests=slide_requests, key_array=team_key_array, iterations=2)

        slide_requests = get_special_keys(value=master_dict[game]["PLAYERS"],
                                          progress_bar=progress_bar, game_number=game_number, requests=slide_requests, key_array=player_key_array, iterations=10)

        slides_service.presentations().batchUpdate(
            presentationId=PRESENTATION_COPY_ID, body={'requests': slide_requests}).execute()

        progress_bar.set_description(f"{game_number} Downloading Images")
        get_images(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID)
        progress_bar.update(1)

        progress_bar.set_description(f"{game_number} Deleting Slides")
        delete_slide(PRESENTATION_COPY_ID)
        progress_bar.update(1)

        game_count += 1
        progress_bar.set_description(f"{game_number} COMPLETE")
        progress_bar.close()


def get_special_keys(value, progress_bar, game_number, requests, key_array, iterations):
    for i in range(iterations):
        for j in range(len(key_array)):
            replacement_key = key_array[j] + str(i+1) + '}'
            progress_bar.set_description(
                f"{game_number} Modifying {replacement_key}")
            replacement_text = value[i].stats_array[j]
            requests = edit_text_request(
                requests, replacement_key, replacement_text)
            progress_bar.update(1)

    return requests


# def get_team_keys(value, progress_bar, game_number, requests):
#     team_key_array = ['{TEAM', '{W-L', '{TP', '{TRT',
#                       '{TFG', '{TA', '{TRB', '{TBL', '{TST', '{TTV', '{TSH']

#     for i in range(2):
#         for j in range(len(team_key_array)):
#             replacement_key = team_key_array[j] + str(i+1) + '}'
#             progress_bar.set_description(
#                 f"{game_number} Modifying Team {i} {replacement_key}")
#             replacement_text = f"{value[i].team_stats_array[j]}"
#             requests = edit_text_request(
#                 requests, replacement_key, replacement_text)
#             progress_bar.update(1)
#             time.sleep(0.05)

#     return requests


def get_slide_id(id):
    presentation = slides_service.presentations().get(presentationId=id).execute()

    slides_data = presentation.get('slides', [])
    slide_ids = []
    for slide in slides_data:
        slide_id = slide['objectId']
        slide_ids.append(slide_id)

    return slide_ids


def copy_slide():

    try:
        drive_response = drive_service.files().copy(
            fileId=PRESENTATION_ID,
            body={'name': 'Copy of Match Details Template'}
        ).execute()

        PRESENTATION_COPY_ID = drive_response.get('id')

    except HttpError as error:
        print(f"An error occurred: {error}")
        print("Presentations not copied")
        return error

    return PRESENTATION_COPY_ID


def edit_text_request(requests, replacement_key, replacement_text):
    requests.append(
        {
            'replaceAllText': {
                'containsText': {
                    'text': replacement_key,
                    'matchCase': False
                },
                'replaceText': replacement_text
            }
        }
    )

    return requests


def edit_image_request(requests, image_id, image_url, slide):
    emu4M = {"magnitude": 4000000, "unit": "EMU"}

    requests.append(
        {
            "createImage": {
                "objectId": image_id,
                "url": image_url,
                "elementProperties": {
                    "pageObjectId": slide,
                    "size": {"height": emu4M, "width": emu4M},
                    "transform": {
                        "scaleX": 1.25,
                        "scaleY": 1.25,
                        "translateX": 2644696,
                        "translateY": 1911096,
                        "unit": "EMU",
                    },
                },
            }
        }
    )
    return requests


def get_images(PRESENTATION_COPY_ID):

    global game_count

    slide_ids = get_slide_id(PRESENTATION_COPY_ID)

    slide_path = []
    slide_count = 1

    game_number = "Game_" + str(game_count)
    all_image_paths[game_number] = []

    for slide in slide_ids:
        thumbnail = slides_service.presentations().pages().getThumbnail(
            presentationId=PRESENTATION_COPY_ID,
            pageObjectId=slide,
        ).execute()

        image_data = thumbnail['contentUrl'].encode()

        response = requests.get(image_data)
        response.raise_for_status()  # Check for any HTTP errors

        # Convert the image content to a PIL Image
        img = Image.open(BytesIO(response.content))

        file_path = game_number + "_P" + str(slide_count) + '.jpg'

        slide_path.append(file_path)

        all_image_paths[game_number].append(file_path)

        img.save(file_path, 'JPEG')

        slide_count += 1

        # print(all_image_paths)
        # print('Image downloaded and saved as JPEG.')

    game_count += 1


def delete_slide(PRESENTATION_COPY_ID):
    try:
        drive_service.files().delete(fileId=PRESENTATION_COPY_ID).execute()
    except Exception as e:
        print(f'Error deleting presentation: {e}')


def remove_all_photos(all_image_paths):
    for key, value in all_image_paths.items():
        print("value: ", value)
        for image_path in value:
            os.remove(image_path)
            print("Image ", image_path, " sucessfully removed.")

    # print("a", all_image_paths)
    # for game in all_image_paths:
    #     print(game)
    #     for image in game:
    #         print(image)
    #         os.remove(image)
    #         print("Image ", image, " removed.")


# with open("catpic.jpg", "wb") as handler:
#         handler.write(image_data)

# with open(f'slide_{slide_id}.png', 'wb') as f:
#     f.write(image_data)

# CONSTANTS.client.update_status_with_media(text="Template", filename="catpic.jpg")

# upload = CONSTANTS.client.media_upload("catpic.jpg")
# CONSTANTS.client.update_status(text="template", media_ids=[upload.media_id_string])


# SLIDE = 'Match Details Template'


# Create a requests list to update text
# requests = [
#     {
#         'replaceAllText': {
#             'containsText': {
#                 'text': '{RT2}',
#                 'matchCase': False
#             },
#             'replaceText': replacement_text
#         }
#     },
#     {

#         'replaceAllText': {
#             'containsText': {
#                 'text': '{RT3}',
#                 'matchCase': False
#             },
#             'replaceText': '124.46'
#         }
#     }
# ]

# def generateScreenshots():

#   presentationId = ID
#   presentation = SlidesApp.openById(presentationId);
#   var baseUrl =
#     "https://slides.googleapis.com/v1/presentations/{presentationId}/pages/{pageObjectId}/thumbnail";
#   var parameters = {
#     method: "GET",
#     headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
#     contentType: "application/json",
#     muteHttpExceptions: true
#   };

#   #Log URL of the main thumbnail of the deck
#   Logger.log(Drive.Files.get(presentationId).thumbnailLink);

#   # For storing the screenshot image URLs
#   screenshots = [];

#   var slides = presentation.getSlides().forEach(function(slide, index) {
#     var url = baseUrl
#       .replace("{presentationId}", presentationId)
#       .replace("{pageObjectId}", slide.getObjectId());
#     var response = JSON.parse(UrlFetchApp.fetch(url, parameters));

#     // Upload Googel Slide image to Google Drive
#     var blob = UrlFetchApp.fetch(response.contentUrl).getBlob();
#     DriveApp.createFile(blob).setName("Image " + (index + 1) + ".png");

#     screenshots.push(response.contentUrl);
#   });

#   return screenshots;


# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload
# from google.oauth2.credentials import Credentials
# import io

# # Replace with your Google Slide ID
# presentation_id = ID
# base_url = "https://slides.googleapis.com/v1/presentations/1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw/pages/p1/thumbnail"

# # Build the Slides API service
# slides_service = build('slides', 'v1', credentials=creds)

# # Get presentation metadata
# presentation_metadata = slides_service.presentations().get(presentationId=presentation_id).execute()
# thumbnail_link = presentation_metadata.get('thumbnailLink')

# # For storing the screenshot image URLs
# screenshots = []

# # Get slides and process them
# slides = presentation_metadata.get('slides', [])
# for index, slide in enumerate(slides):
#     page_object_id = slide['objectId']
#     url = base_url.replace("1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw", presentation_id).replace("p1", page_object_id)
#     response = slides_service.presentations().pages().getThumbnail(presentationId=presentation_id, pageObjectId=page_object_id).execute()

#     # Upload Google Slide image to Google Drive
#     content_url = response.get('contentUrl')
#     image_response = slides_service.presentations().pages().getThumbnailMedia(presentationId=presentation_id, pageObjectId=page_object_id).execute()
#     image_data = MediaIoBaseDownload(io.BytesIO(), image_response)
#     file = DriveApp.createFile("Image " + str(index + 1) + ".png")
#     file.upload_from_file(image_data.fd)

#     screenshots.append(content_url)

# print(screenshots)


# SLIDE_ID = 'p1'


# image_data = thumbnail['content']

# with open(f'slide_{SLIDE_ID}.png', 'wb') as f:
#     f.write(image_data)

# print(f'Slide {SLIDE_ID} image downloaded.')

# Execute the requests
# response = service_slides.presentations().batchUpdate(
#     presentationId=ID, body={'requests': requests}).execute()


# # Load credentials from the JSON file
# credentials = Credentials.from_authorized_user_file('/Users/williamwu/Sterdy/sterdy-permissions.json')

# Now you can make API requests using the slides_service object

# from __future__ import print_function

# from apiclient import discovery
# from httplib2 import Http
# from oauth2client import file, client, tools

# TMP_SLIDE = 'Match Details Template'

# store = file.Storage('storage.json')
# creds = store.get()
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('client-secret.json', SCOPES)
#     creds = tools.run_flow(flow, store)
