from nba_api.stats.endpoints import PlayByPlayV3


class NBA_Player:
    def __init__(self, row) -> None:
        self.data = row
        self.full_name = row["firstName"] + " " + row["familyName"]
        self.last_name = row["familyName"]
        self.person_id = row['personId']
        self.team_tricode = row['teamTricode']
        self.calculate_rating()
        self.get_letter_grade()
        self.stats_array = [self.team_tricode, self.full_name, str(self.rating), str(
            self.pts), str(self.reb), str(self.ast), str(self.blk + self.stl), str(self.plus_minus), str(self.fgm) + "/" + str(self.fga), str(self.ftm) + "/" + str(self.fta), str(round(self.average_shooting_percentage * 100, 1)) + "%", self.letter_grade]

    def calculate_rating(self):
        self.min = self.data['minutes']
        self.fgm = self.data['fieldGoalsMade']
        self.fga = self.data['fieldGoalsAttempted']
        self.fg_pct = self.data['fieldGoalsPercentage']
        self.fg_3_m = self.data['threePointersMade']
        # fg_3_a = self.data['FG3A']
        self.fg_3_pct = self.data['threePointersPercentage']
        self.ftm = self.data['freeThrowsMade']
        self.fta = self.data['freeThrowsAttempted']
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

        total_possible_points = 3 * self.fg_3_m + 2 * self.fga + self.ftm
        if total_possible_points > 0:
            self.average_shooting_percentage = self.pts / total_possible_points
            performance_rating *= (1 + self.average_shooting_percentage)
        else:
            self.average_shooting_percentage = 0

        self.rating = round(performance_rating, 2)

    def player_of_the_match(self):
        text = f"\nPOTG: 🔥#{self.full_name.replace(' ', '')}🔥 ({self.team_tricode})\n"
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

    def get_letter_grade(self):
        if self.rating > 225:
            self.letter_grade = "A+"
        elif self.rating > 160:
            self.letter_grade = "A"
        elif self.rating > 120:
            self.letter_grade = "A-"
        elif self.rating > 100:
            self.letter_grade = "B+"
        elif self.rating > 80:
            self.letter_grade = "B"
        elif self.rating > 60:
            self.letter_grade = "B-"
        elif self.rating > 50:
            self.letter_grade = "C+"
        elif self.rating > 35:
            self.letter_grade = "C"
        elif self.rating > 25:
            self.letter_grade = "C-"
        else:
            self.letter_grade = "D"

    def get_complete_plays(self):
        plays = PlayByPlayV3(self.data["gameId"]).get_data_frames()[0]

        field_goals = [row for index,
                       row in plays.iterrows() if row['personId'] == self.person_id if row['actionType'] == "Made Shot"]

        self.complete_plays = "| "
        for item in field_goals:
            original_string = item["description"].replace(
                self.last_name, "").split("(", 1)[0].strip()

            self.complete_plays += original_string + " | "

        return self.complete_plays
