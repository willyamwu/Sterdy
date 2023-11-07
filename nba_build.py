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

CLIENT_FILE = 'client_secret.json'
CLIENT_ID = CONSTANTS.GOOGLE_CLIENT_ID
CLIENT_SECRET = CONSTANTS.GOOGLE_CLIENT_SECRET
PRESENTATION_ID = '1ZF738FmLMrL22Ig-0c1UqrELf69X60de21fJZV9fpjw'

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

def create_request(master_dict, game_ids, game_dict):
    key_array = ['NAME', 'RATING', 'PTS', 'REB', 'AST', 'DEF', 'TEAM']
    team_key_array = ['TEAM', 'W-L', 'PTS', 'RATING', 'FG', 'SH', 'AST', 'REB', 'BLK', 'STL', 'TOV']

    for game in game_ids:
        game_c = 1
        count = 1
        team_count = 1
        
        PRESENTATION_COPY_ID = create_slide()

        edit_top_slide(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID, game=master_dict[game])

        # for team in master_dict[game]['TEAM']:
        #     print(team)
        #     for i in range(len(team_key_array)):
        #         get_team_keys(key=team_key_array[i], value=team, i=team_count, PRESENTATION_COPY_ID=PRESENTATION_COPY_ID)
        #         time.sleep(1)
        #     team_count+=1

        for players in master_dict[game]['PLAYERS']:
                print(players)
                for i in range(7):
                    get_special_keys(key=key_array[i], value=players, i=count, PRESENTATION_COPY_ID=PRESENTATION_COPY_ID)
                    time.sleep(1)

        get_images(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID)
        delete_slide(PRESENTATION_COPY_ID)
    print(requests)


def get_special_keys(key, value, i, PRESENTATION_COPY_ID):
    if key == 'NAME':
        replacement_key = '{' + key + str(i) + '}'
        value = value.data['firstName'] + " " + value.data['familyName']
    elif key == 'RATING':
        replacement_key = '{' + 'RT' + str(i) + '}'
        value = value.rating
    elif key == 'PTS':
        replacement_key = '{' + 'P' + str(i) + '}'
        value = value.data['points']
    elif key == 'REB':
        replacement_key = '{' + 'RB' + str(i) + '}'
        value = value.data['reboundsTotal']
    elif key == 'AST':
        replacement_key = '{' + 'A' + str(i) + '}'
        value = value.data['assists']
    elif key == 'DEF':
        replacement_key = '{' + 'D' + str(i) + '}'
        value = value.data['steals'] + value.data['blocks'] 
    elif key == 'TEAM':
        replacement_key = '{' + 'T' + str(i) + '}'
        value = value.data['teamTricode']
    else:
       return

    # request = [
    #     {
    #         'replaceAllText': {
    #             'containsText': {
    #                 'text': replacement_key,
    #                 'matchCase': False
    #             },
    #             'replaceText': str(value)
    #         }
    #     }
    # ]

    edit_text_slide(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID, replacement_key=replacement_key, replacement_text=str(value))


def get_team_keys(key, value, i, PRESENTATION_COPY_ID):
    if key == 'TEAM':
        replacement_key = '{' + key + str(i) + '}'
        value = value.data['firstName'] + " " + value.data['familyName']
    elif key == 'W-L':
        replacement_key = '{' + 'RT' + str(i) + '}'
        value = value.rating
    elif key == 'PTS':
        replacement_key = '{' + 'P' + str(i) + '}'
        value = value.data['points']
    elif key == 'REB':
        replacement_key = '{' + 'RB' + str(i) + '}'
        value = value.data['reboundsTotal']
    elif key == 'AST':
        replacement_key = '{' + 'A' + str(i) + '}'
        value = value.data['assists']
    elif key == 'DEF':
        replacement_key = '{' + 'D' + str(i) + '}'
        value = value.data['steals'] + value.data['blocks'] 
    elif key == 'TEAM':
        replacement_key = '{' + 'T' + str(i) + '}'
        value = value.data['teamTricode']
    else:
       return

    edit_text_slide(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID, replacement_key=replacement_key, replacement_text=str(value))


def get_slide_id(id):
    presentation = slides_service.presentations().get(presentationId=id).execute()

    slides_data = presentation.get('slides', [])
    slide_ids = []
    for slide in slides_data:
        slide_id = slide['objectId']
        slide_ids.append(slide_id)
    
    return slide_ids


def create_slide():

    try:
        drive_response = drive_service.files().copy(
            fileId=PRESENTATION_ID, 
            body = {'name': 'Copy of Match Details Template'}
        ).execute()
        
        PRESENTATION_COPY_ID = drive_response.get('id')

    except HttpError as error:
        print(f"An error occurred: {error}")
        print("Presentations  not copied")
        return error
    
    print(f'Copy of presentation created with ID: {PRESENTATION_COPY_ID}')
    return PRESENTATION_COPY_ID


def edit_text_slide(PRESENTATION_COPY_ID, replacement_key, replacement_text):
    request = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': replacement_key,
                    'matchCase': False
                },
                'replaceText': replacement_text
            }
        }
    ]

    response = slides_service.presentations().batchUpdate(
        presentationId=PRESENTATION_COPY_ID, body={'requests': request}).execute()


def edit_top_slide(PRESENTATION_COPY_ID, game):
    # requests = [
    #     {
    #         'replaceAllText': {
    #             'containsText': {
    #                 'text': '{{MATCH}}',
    #                 'matchCase': False
    #             },
    #             'replaceText': game['SLIDE_MATCHUP']
    #         }
    #     }
    # ]

    edit_text_slide(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID, replacement_key='{{MATCH}}', replacement_text=game['SLIDE_MATCHUP'])

    # requests = [
    #     {
    #         'replaceAllText': {
    #             'containsText': {
    #                 'text': '{DATE}',
    #                 'matchCase': False
    #             },
    #             'replaceText': CONSTANTS.yesterday_date_string
    #         }
    #     }
    # ]

    edit_text_slide(PRESENTATION_COPY_ID=PRESENTATION_COPY_ID, replacement_key='{DATE}', replacement_text=CONSTANTS.yesterday_date_string)


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


        file_path = game_number +  "_P" + str(slide_count) + '.jpg'

        slide_path.append(file_path)

        all_image_paths[game_number].append(file_path)

        img.save(file_path, 'JPEG')
        
        slide_count += 1

        print(all_image_paths)
        print('Image downloaded and saved as JPEG.')

    game_count += 1


def delete_slide(PRESENTATION_COPY_ID):
        try:
            drive_service.files().delete(fileId=PRESENTATION_COPY_ID).execute()
            print(f'Presentation with ID {PRESENTATION_COPY_ID} deleted successfully.')
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
