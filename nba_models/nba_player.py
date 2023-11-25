class NBA_Player:
    def __init__(self, row) -> None:
        self.data = row
        self.full_name = row["firstName"] + " " + row["familyName"]
        self.last_name = row["familyName"]
        self.person_id = row['personId']
        self.team_tricode = row['teamTricode']
        self.calculate_rating()
        self.stats_array = [self.team_tricode, self.full_name, str(self.rating), str(
            self.pts), str(self.reb), str(self.ast), str(self.blk + self.stl)]

    def calculate_rating(self):
        self.min = self.data['minutes']
        self.fgm = self.data['fieldGoalsMade']
        # fga = self.data['FGA']
        self.fg_pct = self.data['fieldGoalsPercentage']
        self.fg_3_m = self.data['threePointersMade']
        # fg_3_a = self.data['FG3A']
        self.fg_3_pct = self.data['threePointersPercentage']
        self.ftm = self.data['freeThrowsMade']
        # fta = self.data['FTA']
        self.ft_pct = self.data['freeThrowsPercentage']
        self.reb = self.data['reboundsTotal']
        self.ast = self.data['assists']
        self.stl = self.data['steals']
        self.blk = self.data['blocks']
        self.tov = self.data['turnovers']
        self.pts = self.data['points']
        self.plus_minus = self.data['plusMinusPoints']

        performance_rating = (
            self.pts * 1.5 + self.reb * 0.75 + self.ast * 1.25 +
            self.fgm + self.fg_3_m * 1.5 + self.ftm * 0.5 +
            self.stl * 1.75 + self.blk * 1.75 -
            self.tov * 2 +
            self.plus_minus
        )

        self.average_shooting_percentage = (
            self.fg_pct * 2 + self.fg_3_pct * 3 + self.ft_pct) / 6
        performance_rating *= (1 + self.average_shooting_percentage)

        self.rating = round(performance_rating, 2)

    def player_of_the_match(self):
        text = f"\nPOTG: 🔥{self.full_name.upper()}🔥 ({self.team_tricode})\n"
        text += f"{self.rating} RATING\n"

        if self.pts > 0:
            text += f"{self.pts} PTS\n"
        if self.ast > 0:
            text += f"{self.ast} AST\n"
        if self.reb > 0:
            text += f"{self.reb} REB\n"
        if self.stl > 0:
            text += f"{self.stl} STL\n"
        if self.blk > 0:
            text += f"{self.blk} BLK\n"
        if self.plus_minus > 0:
            text += f"+{self.plus_minus} +/-\n"

        return text
