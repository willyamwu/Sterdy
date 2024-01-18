import time
import CONSTANTS
from tqdm import tqdm

GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

def twitter_post(all_image_paths, master_dict, unique_games, caption):
    progress_bar = tqdm(total=len(unique_games) + 1, bar_format=f"{{l_bar}}{GREEN}{{bar}}{RESET_COLOR}{{r_bar}}", desc="Posting to X", unit="task")

    progress_bar.set_description("Getting Matchups")
    twitter_matchups = []
    count = 0
    for game in unique_games:
        twitter_matchups.append(master_dict[game][caption])

    progress_bar.update(1)

    for key, value in all_image_paths.items():
        progress_bar.set_description(f"Posting Game {count}")


        # media_ids = []

        # res = CONSTANTS.api.media_upload(value[0])
        # media_ids.append(res)


        media_ids = []
        for image_path in value:
            res = CONSTANTS.api.media_upload(image_path)
            media_ids.append(res.media_id)

        CONSTANTS.client.create_tweet(text=twitter_matchups[count], media_ids=media_ids)
        count += 1
        progress_bar.update(1)
        time.sleep(1)


            # CONSTANTS.client.update_status_with_media(text="Template", filename="catpic.jpg")
    progress_bar.set_description("Posting COMPLETE")
    progress_bar.close()

# upload = CONSTANTS.client.media_upload("catpic.jpg")
# CONSTANTS.client.update_status(text="template", media_ids=[upload.media_id_string])


