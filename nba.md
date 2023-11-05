# NBA Sterdy Project

A script that pulls data from [nba_api](https://github.com/swar/nba_api) by swar to get the latest analysis on NBA games and the performance of players.

This data is then fed through the Google Slides API to build a social media post template. After building, it links to the tweepy API to post these photos on X.

## nba_data.py

This contains a script that pulls data to get the offensive and defensive stats of a player and a team for the most recent games.

It uses the [BoxScoreTraditionalV3](https://github.com/swar/nba_api/blob/79ed980e4da4d19e55701cd83c74c2570be1c1b5/src/nba_api/stats/endpoints/boxscoretraditionalv3.py#L12), [LeagueGameFinder](https://github.com/swar/nba_api/blob/64208a57c9b5de63afedc6b1e8445fc75d29b061/src/nba_api/stats/endpoints/leaguegamefinder.py#L6), and BoxScoreDefensiveV2.

## nba_build.py

## nba_post.py
