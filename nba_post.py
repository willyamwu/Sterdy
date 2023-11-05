import time
import CONSTANTS

def twitter_post(all_image_paths, master_dict, unique_games):
    print(all_image_paths)
    twitter_matchups = []
    count = 0
    for game in unique_games:
        twitter_matchups.append(master_dict[game]['TWITTER_MATCHUP'])

    for key, value in all_image_paths.items():
        print("value: ", value)
        media_ids = []
        for image_path in value:
            print(image_path)
            res = CONSTANTS.api.media_upload(image_path)
            media_ids.append(res.media_id)

        CONSTANTS.client.create_tweet(text=twitter_matchups[count], media_ids=media_ids)
        count += 1
        time.sleep(1)


            # CONSTANTS.client.update_status_with_media(text="Template", filename="catpic.jpg")

# upload = CONSTANTS.client.media_upload("catpic.jpg")
# CONSTANTS.client.update_status(text="template", media_ids=[upload.media_id_string])


