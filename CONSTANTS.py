import tweepy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Twitter Keys
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_KEY_SECRET = os.environ['TWITTER_API_KEY_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

# Google Cloud Keys
GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']


# INSTAGRAM_APP_SECRET = '2bb3b4aa672a5e4d2c86c7264ab0e559'
# INSTAGRAM_ACCESS_TOKEN = 'EAAmwYHbVE58BOy8RRkNf0IiIRIZAvu7lT6Hmolkpwcvl5ymmJwaZBkrZAnMNvV6y9yPHJs6cVxFgpd0Ln9gj1bGZBWzBXVxFYnEzzKusvpxILOhd410E64eDXKGpKGQcrM8S3Q88a27TGu6jgYL9RZCZAnB2japtgHiF9RnLMWW1jAZB1mZB6jJRMwwqg5ctzIr8UBBZCfM0cwjhnnPdcaQo38dnkDNzzy7AmdV8ZD'
# id = "122112222596018957"
# business_id = "123612720831100"
# insta_business_id = "111274578741163"

start_up_prompt = '''Command Options:
(1) Daily Game Analysis
(2) Player Rankings 
(3) Team Rankings'''

# Twitter Authentication
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET )
api = tweepy.API(auth)

client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_KEY_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET 
)


current_date = datetime.now()   # Get the current date and time
current_date_string = current_date.strftime('%Y-%m-%d')    # Format the current date as a string

yesterday_date = current_date - timedelta(days=1)   # Calculate yesterday's date
yesterday_date_string = yesterday_date.strftime('%m/%d/%Y')    # Format yesterday's date as a string

# yesterday_date_string = '4/18/2023'