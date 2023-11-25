from nba_api.stats.endpoints import TeamYearByYearStats


class NBA_Team:

    def __init__(self, data):
        self.data = data
        self.team_id = data['teamId']
        self.team_name = data['teamName']
        self.team_city = data['teamCity']
        self.team_tricode = data['teamTricode']
        self.team_slug = data['teamSlug']
        self.calculate_rating()
        self.get_season_stats()
        self.stats_array = [f"{self.team_slug.title()}{self.conference_ranking}", f"{str(self.wins)}-{str(self.loses)}", str(self.pts), str(self.rating), self.fg, str(
            self.ast), str(self.reb), str(self.blk), str(self.stl), str(self.tov), str(self.average_shooting_percentage) + "%"]

    def calculate_rating(self):
        self.pts = self.data['points']
        self.fgm = self.data['fieldGoalsMade']
        self.fga = self.data['fieldGoalsAttempted']
        self.fg = str(self.fgm) + "/" + str(self.fga)
        self.fg_pct = self.data['fieldGoalsPercentage']
        self.fg_3_m = self.data['threePointersMade']
        # fg_3_a = self.data['threePointersAttempted']
        self.fg_3_pct = self.data['threePointersPercentage']
        self.ftm = self.data['freeThrowsMade']
        # fta = self.data['freeThrowsAttempted']
        self.ft_pct = self.data['freeThrowsPercentage']
        self.reb = self.data['reboundsTotal']
        self.ast = self.data['assists']
        self.stl = self.data['steals']
        self.blk = self.data['blocks']
        self.tov = self.data['turnovers']

        performance_rating = (
            self.pts * 1.5 + self.reb * 0.75 + self.ast * 1.25 +
            self.fgm + self.fg_3_m * 1.5 + self.ftm * 0.5 +
            self.stl * 1.75 + self.blk * 1.75 -
            self.tov * 2
        )

        # Calculate the team shooting percentages bonus
        self.average_shooting_percentage = (
            self.fg_pct * 2 + self.fg_3_pct * 3 + self.ft_pct) / 6
        performance_rating *= (1 + self.average_shooting_percentage)
        self.average_shooting_percentage = round(
            self.average_shooting_percentage * 100, 2)

        # Divide the total rating by 5 to identify average team performance.
        self.rating = round(performance_rating / 5, 2)

    def get_season_stats(self):
        season_stats = TeamYearByYearStats(team_id=self.team_id)
        season_stats_df = season_stats.get_data_frames()[0].iloc[-1]
        self.wins = season_stats_df["WINS"]
        self.loses = season_stats_df["LOSSES"]
        self.win_pct = season_stats_df["WIN_PCT"]
        self.conference_ranking = self.int_to_superscript(
            season_stats_df["CONF_RANK"])

    def int_to_superscript(self, num):
        superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
        return str(num).translate(superscript_digits)
