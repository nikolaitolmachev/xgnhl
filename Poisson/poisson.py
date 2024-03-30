import math, Poisson.probability as probability, Services.consts as consts
from Entities.bookmaker_moneyline import BookmakerMoneyline
from Entities.bookmaker_total import BookmakerTotal
from Entities.bookmaker_handicap import BookmakerHandicap

class Poisson:
    """
    Poisson distribution сlass creates a probability table of score goals of teams and draws.

    :var home: quality of home team.
    :var away: quality of away team.
    :var probability_table_goal_draws: probability table of score goals of teams and draws
    """

    def __init__(self, quality_team_A, quality_team_B):

        self.__home = quality_team_A
        self.__away = quality_team_B
        self.__probability_table_goal_draws = self.__create_probability_table()

    @property
    def home(self):
        return self.__home

    @property
    def away(self):
        return self.__away

    @property
    def probability_table_goal_draws(self):
        return self.__probability_table_goal_draws

    @property
    def poisson_totals(self):
        return self.__poisson_totals

    def __calculate_goal_probability(self, _lambda: float, k: int) -> probability.Probability:
        """
        Returns a goal probability for a team by given lambda for expected k.

        :param _lambda: mathematical expectation of a random variable.
        :param k: number of events.
        :return: type Probability.
        """
        probability_k = (_lambda ** k * math.exp(-_lambda)) / (math.factorial(k))
        result = probability.Probability(round(probability_k, 3))
        return result

    def __calculate_draw_probability(self, goal_probability_home: float, goal_probability_away: float) -> probability.Probability:
        """
        Returns a probability of a draw by goal probabilities of home and away teams.

        :param goal_probability_home: probability of home goal.
        :param goal_probability_away: probability of away goal.
        :return: type Probability.
        """
        draw_probability = goal_probability_home * goal_probability_away
        result = probability.Probability(round(draw_probability, 3))
        return result

    def __create_probability_table(self):
        """
        Creates a probability table which consists of goal probabilities of both teams and probability of a draws.

        :return list of goal probabilities of both teams and probability of a draws.
        """
        probability_table = [[0] * consts.MAX_SCORE_HOCKEY for i in range(consts.SUM_OF_RESULTS_1_X_2)]

        for i in range(consts.SUM_OF_RESULTS_1_X_2):
            for j in range(consts.MAX_SCORE_HOCKEY):
                if i != consts.SUM_OF_RESULTS_1_X_2 - 1:
                    if i == 0:
                        probability_table[i][j] = self.__calculate_goal_probability(self.__home, j)
                    else:
                        probability_table[i][j] = self.__calculate_goal_probability(self.__away, j)
                else:
                    goal_probability_home = probability_table[i - 2][j]
                    goal_probability_away = probability_table[i - 1][j]
                    probability_table[i][j] = self.__calculate_draw_probability(goal_probability_home,
                                                                                goal_probability_away)
        #print(probability_table)
        return probability_table

    def calculate_total_odds_by_Poisson(self) -> dict:
        """
        Calculates lines of total and their odds (Over/Under) by a Poisson probability table.

        :return dict where key = BookmakerTotal.line and value = BookmakerTotal.
        """

        list_of_totals = []

        # calculate 0.5, 1.5, 2.5 ... 8.5 lines

        under = self.__probability_table_goal_draws[2][0].probability
        if under == 0.0:
            under = consts.ALMOST_0
        list_of_totals.append(BookmakerTotal(0.5, self.__get_over_odds(under), round(1 / under, 3)))

        under = self.__probability_table_goal_draws[2][0] + self.__probability_table_goal_draws[0][1] * \
                self.__probability_table_goal_draws[1][0] + self.__probability_table_goal_draws[0][0] * \
                self.__probability_table_goal_draws[1][1]
        if under == 0.0:
            under = consts.ALMOST_0
        list_of_totals.append(BookmakerTotal(1.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[2][1] + self.__probability_table_goal_draws[0][2] * \
                 self.__probability_table_goal_draws[1][0] + self.__probability_table_goal_draws[0][0] * \
                 self.__probability_table_goal_draws[1][2]
        list_of_totals.append(BookmakerTotal(2.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += round(self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][1] +
                       self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][2] +
                       self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][0] +
                       self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][3], 4)
        list_of_totals.append(BookmakerTotal(3.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[2][2] + self.__probability_table_goal_draws[0][3] * \
                 self.__probability_table_goal_draws[1][1] + self.__probability_table_goal_draws[0][1] * \
                 self.__probability_table_goal_draws[1][3] + self.__probability_table_goal_draws[0][4] * \
                 self.__probability_table_goal_draws[1][0] + self.__probability_table_goal_draws[0][0] * \
                 self.__probability_table_goal_draws[1][4]
        list_of_totals.append(BookmakerTotal(4.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][2] + \
                 self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][3] + \
                 self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][1] + \
                 self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][4] + \
                 self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][0] + \
                 self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][5]
        list_of_totals.append(BookmakerTotal(5.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[2][3] + self.__probability_table_goal_draws[0][6] * \
                 self.__probability_table_goal_draws[1][0] + self.__probability_table_goal_draws[0][0] * \
                 self.__probability_table_goal_draws[1][6] + self.__probability_table_goal_draws[0][5] * \
                 self.__probability_table_goal_draws[1][1] + self.__probability_table_goal_draws[0][1] * \
                 self.__probability_table_goal_draws[1][5] + self.__probability_table_goal_draws[0][4] * \
                 self.__probability_table_goal_draws[1][2] + self.__probability_table_goal_draws[0][2] * \
                 self.__probability_table_goal_draws[1][4]
        list_of_totals.append(BookmakerTotal(6.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][3] + \
                 self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][4] + \
                 self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][2] + \
                 self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][5] + \
                 self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][1] + \
                 self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][6] + \
                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[0][0] + \
                 self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][7]
        list_of_totals.append(BookmakerTotal(7.5, self.__get_over_odds(under), round(1 / under, 3)))

        under += self.__probability_table_goal_draws[2][4] + self.__probability_table_goal_draws[0][8] * \
                 self.__probability_table_goal_draws[1][0] + self.__probability_table_goal_draws[0][0] * \
                 self.__probability_table_goal_draws[1][8] + self.__probability_table_goal_draws[0][7] * \
                 self.__probability_table_goal_draws[1][1] + self.__probability_table_goal_draws[0][1] * \
                 self.__probability_table_goal_draws[1][7] + self.__probability_table_goal_draws[0][6] * \
                 self.__probability_table_goal_draws[1][2] + self.__probability_table_goal_draws[0][2] * \
                 self.__probability_table_goal_draws[1][6]
        list_of_totals.append(BookmakerTotal(8.5, self.__get_over_odds(under), round(1 / under, 3)))

        # calculate 1.0, 2.0, 3.00 ... 8.00 lines
        under1 = round(1 / ((1 / list_of_totals[0].odds_under) / (1 / list_of_totals[0].odds_under + 1 / list_of_totals[1].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(1, self.__get_over_odds(1 / under1), under1))

        under2 = round(1 / ((1/list_of_totals[1].odds_under) / (1/list_of_totals[1].odds_under + 1/list_of_totals[2].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(2, self.__get_over_odds(1 / under2), under2))

        under3 = round(1 / ((1/list_of_totals[2].odds_under) / (1/list_of_totals[2].odds_under + 1/list_of_totals[3].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(3, self.__get_over_odds(1 / under3), under3))

        under4 = round(1 / ((1 / list_of_totals[3].odds_under) / (1 / list_of_totals[3].odds_under + 1 / list_of_totals[4].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(4, self.__get_over_odds(1 / under4), under4))

        under5 = round(1 / ((1 / list_of_totals[4].odds_under) / (1 / list_of_totals[4].odds_under + 1 / list_of_totals[5].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(5, self.__get_over_odds(1 / under5), under5))

        under6 = round(1 / ((1 / list_of_totals[5].odds_under) / (1 / list_of_totals[5].odds_under + 1 / list_of_totals[6].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(6, self.__get_over_odds(1 / under6), under6))

        under7 = round(1 / ((1 / list_of_totals[6].odds_under) / (1 / list_of_totals[6].odds_under + 1 / list_of_totals[7].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(7, self.__get_over_odds(1 / under7), under7))

        under8 = round(1 / ((1 / list_of_totals[7].odds_under) / (1 / list_of_totals[7].odds_under + 1 / list_of_totals[8].odds_over)), 3)
        list_of_totals.append(BookmakerTotal(8, self.__get_over_odds(1 / under8), under8))

        list_of_totals = sorted(list_of_totals, key=lambda bookmaker_total: bookmaker_total.line)

        # calculate 0.75, 1.25, 1.75, 2.25 ... 8.25 lines
        i = 1
        asian_lines = []
        for bt in list_of_totals:
            try:
                asian_total_line = self.__get_asian_total_line(bt, list_of_totals[i])
                asian_lines.append(asian_total_line)
                i += 1
            except IndexError:
                break
        list_of_totals += asian_lines
        list_of_totals = sorted(list_of_totals, key=lambda bookmaker_total: bookmaker_total.line)

        # create dict
        dict_totals = {}
        for total in list_of_totals:
            dict_totals[total.line] = total

        return dict_totals

    def __get_over_odds(self, under: float) -> float:
        """
        Calculates odds of Over by probability of Under.

        :param under: probability of Under.
        :return: odds of Over.
        """
        over_probability = round(1.00 - under, 3)
        over_odds = round(1 / over_probability, 3)
        return over_odds

    def __get_asian_total_line(self, line_1: BookmakerTotal, line_2: BookmakerTotal) -> BookmakerTotal:
        """
        Calculates asian total line.

        :param line_1: type BookmakerTotal #1.
        :param line_2: type BookmakerTotal #2.
        :return: type BookmakerTotal.
        """

        line = round((line_1.line + line_2.line) / 2, 2)
        over = round((line_1.odds_over + line_2.odds_over) / 2, 3)
        under = round((line_1.odds_under + line_2.odds_under) / 2, 3)
        return BookmakerTotal(line, over, under)

    def calculate_moneyline_by_Poisson(self) -> BookmakerMoneyline:
        """
        Calculates bookmaker moneyline by a Poisson probability table.

        :return type BookmakerMoneyline.
        """

        moneyline_poisson = None

        # calculate odds for home win
        home_odds = consts.ALMOST_0
        i, j = 1, 0
        for _ in range(0, 6):
            for _ in range(0, 6):
                if i != j:
                    res = self.__probability_table_goal_draws[0][i] * self.__probability_table_goal_draws[1][j]
                    home_odds += res
                    j += 1
            i += 1
            j = 0
        home_odds = round(1/home_odds, 3)

        # calculate odds for a draw
        draw_odds = consts.ALMOST_0
        for draw in self.__probability_table_goal_draws[2]:
            draw_odds += draw.probability
        draw_odds = round(1/draw_odds, 3)

        # calculate odds for away win
        away_odds = consts.ALMOST_0
        i, j = 0, 1
        for _ in range(0, 6):
            for _ in range(0, 6):
                if i != j:
                    res = self.__probability_table_goal_draws[0][i] * self.__probability_table_goal_draws[1][j]
                    away_odds += res
                    i += 1
            j += 1
            i = 0
        away_odds = round(1 / away_odds, 3)

        moneyline_poisson = BookmakerMoneyline(home_odds, draw_odds, away_odds)
        return moneyline_poisson

    def calculate_handicap_odds_by_Poisson(self, moneyline: BookmakerMoneyline) -> dict:
        """
        Calculates lines of handicap and their odds by a Poisson probability table.

        :param moneyline: type of BookmakerMoneyline.
        :return dict where key = BookmakerHandicap.line and value = BookmakerHandicap.
        """

        list_of_handicaps = []

        # calculate -7.5, -6.5, -5.5 ... +7.5 lines
        # -7.5 = 8-0
        try:
            handicap_minus_7_5 = self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][0]
            list_of_handicaps.append(BookmakerHandicap(-7.5, round(1 / handicap_minus_7_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_7_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_7_5 = consts.ALMOST_0

        # -6.5 = 7-0, 8-0, 8-1
        try:
            handicap_minus_6_5 = self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][1] + \
                                 handicap_minus_7_5
            list_of_handicaps.append(BookmakerHandicap(-6.5, round(1 / handicap_minus_6_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_6_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_6_5 = consts.ALMOST_0

        # -5.5 = 6-0, 7-0, 7-1, 8-0, 8-1, 8-2
        try:
            handicap_minus_5_5 = self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][1] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][2] + \
                                 handicap_minus_6_5
            list_of_handicaps.append(BookmakerHandicap(-5.5, round(1 / handicap_minus_5_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_5_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_5_5 = consts.ALMOST_0

        # -4.5 = 5-0, 6-0, 6-1, 7-0, 7-1, 7-2, 8-0, 8-1, 8-2, 8-3
        try:
            handicap_minus_4_5 = self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][1] + \
                                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][2] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][3] + \
                                 handicap_minus_5_5
            list_of_handicaps.append(BookmakerHandicap(-4.5, round(1 / handicap_minus_4_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_4_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_4_5 = consts.ALMOST_0

        # -3.5 = 4-0, 5-0, 5-1, 6-0, 6-1, 6-2, 7-0, 7-1, 7-2, 7-3, 8-0, 8-1, 8-2, 8-3, 8-4
        try:
            handicap_minus_3_5 = self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][1] + \
                                 self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][2] + \
                                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][3] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][4] + \
                                 handicap_minus_4_5
            list_of_handicaps.append(BookmakerHandicap(-3.5, round(1 / handicap_minus_3_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_3_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_3_5 = consts.ALMOST_0

        # -2.5 = 3-0, 4-0, 4-1, 5-0, 5-1, 5-2, 6-0, 6-1, 6-2, 6-3, 7-0, 7-1, 7-2, 7-3, 7-4, 8-0, 8-1, 8-2, 8-3, 8-4. 8-5
        try:
            handicap_minus_2_5 = self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][1] + \
                                 self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][2] + \
                                 self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][3] + \
                                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][4] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][5] + \
                                 handicap_minus_3_5
            list_of_handicaps.append(BookmakerHandicap(-2.5, round(1 / handicap_minus_2_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_2_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_2_5 = consts.ALMOST_0

        # -1.5 = 2-0, 3-0, 3-1, 4-0, 4-1, 4-2, 5-0, 5-1, 5-2, 5-3, 6-0, 6-1, 6-2, 6-3, 6-4
        #      = 7-0, 7-1, 7-2, 7-3, 7-4, 7-5, 8-0, 8-1, 8-2, 8-3, 8-4, 8-5, 8-6
        try:
            handicap_minus_1_5 = self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][0] + \
                                 self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][1] + \
                                 self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][2] + \
                                 self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][3] + \
                                 self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][4] + \
                                 self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][5] + \
                                 self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][6] + \
                                 handicap_minus_2_5
            list_of_handicaps.append(BookmakerHandicap(-1.5, round(1 / handicap_minus_1_5, 3),
                                                       self.__get_opposite_handicap_odds(handicap_minus_1_5)))
        except (ZeroDivisionError, ValueError):
            handicap_minus_1_5 = consts.ALMOST_0

        # -0.5 = Moneyline home win
        list_of_handicaps.append(BookmakerHandicap(-0.5, moneyline.odds_home,
                                                   self.__get_opposite_handicap_odds(1 / moneyline.odds_home)))

        # +0
        handicap_0_home_odds = round((1 - (1 / moneyline.odds_draw)) / (1 / moneyline.odds_home), 3)
        handicap_0_away_odds = round((1 - (1 / moneyline.odds_draw)) / (1 / moneyline.odds_away), 3)
        list_of_handicaps.append(BookmakerHandicap(0, handicap_0_home_odds, handicap_0_away_odds))

        # +0.5 = Moneyline away win
        list_of_handicaps.append(BookmakerHandicap(0.5,
                                    self.__get_opposite_handicap_odds(1 / moneyline.odds_away), moneyline.odds_away))

        # +7.5 = 0-8
        try:
            handicap_plus_7_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][8]
            list_of_handicaps.append(BookmakerHandicap(7.5, self.__get_opposite_handicap_odds(handicap_plus_7_5),
                                                       round(1 / handicap_plus_7_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_7_5 = consts.ALMOST_0

        # +6.5 = 0-7, 0-8, 1-8
        try:
            handicap_plus_6_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_7_5
            list_of_handicaps.append(BookmakerHandicap(6.5, self.__get_opposite_handicap_odds(handicap_plus_6_5),
                                                       round(1 / handicap_plus_6_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_6_5 = consts.ALMOST_0

        # +5.5 = 0-6, 0-7, 1-7, 0-8, 1-8, 2-8
        try:
            handicap_plus_5_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][6] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_6_5
            list_of_handicaps.append(BookmakerHandicap(5.5, self.__get_opposite_handicap_odds(handicap_plus_5_5),
                                                       round(1 / handicap_plus_5_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_5_5 = consts.ALMOST_0

        # +4.5= 0-5, 0-6, 1-6, 0-7, 1-7, 2-7, 0-8, 1-8, 2-8, 3-8
        try:
            handicap_plus_4_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][5] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][6] + \
                                self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_5_5
            list_of_handicaps.append(BookmakerHandicap(4.5, self.__get_opposite_handicap_odds(handicap_plus_4_5),
                                                       round(1 / handicap_plus_4_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_4_5 = consts.ALMOST_0

        # +3.5 = 0-4, 0-5, 1-5, 0-6, 1-6, 2-6, 0-7, 1-7, 2-7, 3-7, 0-8, 1-8, 2-8, 3-8, 4-8
        try:
            handicap_plus_3_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][4] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][5] + \
                                self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][6] + \
                                self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_4_5
            list_of_handicaps.append(BookmakerHandicap(3.5, self.__get_opposite_handicap_odds(handicap_plus_3_5),
                                                       round(1 / handicap_plus_3_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_3_5 = consts.ALMOST_0

        # +2.5 = 0-3, 0-4, 1-4, 0-5, 1-5, 2-5, 0-6, 1-6, 2-6, 3-6
        #      = 0-7, 1-7, 2-7, 3-7, 4-7, 0-8, 1-8, 2-8, 3-8, 4-8, 5-8
        try:
            handicap_plus_2_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][3] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][4] + \
                                self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][5] + \
                                self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][6] + \
                                self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_3_5

            list_of_handicaps.append(BookmakerHandicap(2.5, self.__get_opposite_handicap_odds(handicap_plus_2_5),
                                                       round(1 / handicap_plus_2_5, 3)))
        except (ZeroDivisionError, ValueError):
            handicap_plus_2_5 = consts.ALMOST_0


        # +1.5 = 0-2, 0-3, 1-3, 0-4, 1-4, 2-4, 0-5, 1-5, 2-5, 3-5, 0-6, 1-6, 2-6, 3-6, 4-6
        #      = 0-7, 1-7, 2-7, 3-7, 4-7, 5-7, 0-8, 1-8, 2-8. 3-8, 4-8, 5-8, 6-8
        try:
            handicap_plus_1_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][2] + \
                                self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][3] + \
                                self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][4] + \
                                self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][5] + \
                                self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][6] + \
                                self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][7] + \
                                self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][8] + \
                                handicap_plus_2_5
            list_of_handicaps.append(BookmakerHandicap(1.5,
                                self.__get_opposite_handicap_odds(handicap_plus_1_5), round(1 / handicap_plus_1_5, 3)))
        except (ZeroDivisionError, ValueError):
            pass


        # calculate -8, -7, -6 ... -1 lines
        try:
            home_win_by_1 = self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][7]

            home_odds = round((1 - home_win_by_1) / ((1 / moneyline.odds_home) - home_win_by_1), 3)
            away_odds = round((1 - home_win_by_1) / (1 - (1 / moneyline.odds_home)), 3)
            list_of_handicaps.append(BookmakerHandicap(-1.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_2 = self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][6]

            home_odds = round((1 - home_win_by_2) / ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2), 3)
            away_odds = round((1 - home_win_by_2) / (1 - (1 / moneyline.odds_home) + home_win_by_1), 3)
            list_of_handicaps.append(BookmakerHandicap(-2.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_3 = self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][5]
            home_odds = round((1 - home_win_by_3) /
                              ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 - home_win_by_3), 3)
            away_odds = round((1 - home_win_by_3) / (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2), 3)
            list_of_handicaps.append(BookmakerHandicap(-3.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_4 = self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][4]
            home_odds = round((1 - home_win_by_4) /
                        ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 - home_win_by_3 - home_win_by_4), 3)
            away_odds = round((1 - home_win_by_4) /
                        (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2 + home_win_by_3), 3)
            list_of_handicaps.append(BookmakerHandicap(-4.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_5 = self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][3]
            home_odds = round((1 - home_win_by_5) / ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 -
                                                     home_win_by_3 - home_win_by_4 - home_win_by_5), 3)
            away_odds = round((1 - home_win_by_5) / (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2 +
                                                     home_win_by_3 + home_win_by_4), 3)
            list_of_handicaps.append(BookmakerHandicap(-5.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_6 = self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][2]
            home_odds = round((1 - home_win_by_6) / ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 -
                                                     home_win_by_3 - home_win_by_4 - home_win_by_5 - home_win_by_6), 3)
            away_odds = round((1 - home_win_by_6) / (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2
                                                     + home_win_by_3 + home_win_by_4 + home_win_by_5), 3)
            list_of_handicaps.append(BookmakerHandicap(-6.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_7 = self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][0] + \
                            self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][1]
            home_odds = round((1 - home_win_by_7) / ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 -
                                    home_win_by_3 - home_win_by_4 - home_win_by_5 - home_win_by_6 - home_win_by_7), 3)
            away_odds = round((1 - home_win_by_7) / (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2 +
                                                    home_win_by_3 + home_win_by_4 + home_win_by_5 + home_win_by_6), 3)
            list_of_handicaps.append(BookmakerHandicap(-7.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            home_win_by_8 = self.__probability_table_goal_draws[0][8] * self.__probability_table_goal_draws[1][0]
            home_odds = round((1 - home_win_by_8) / ((1 / moneyline.odds_home) - home_win_by_1 - home_win_by_2 -
                    home_win_by_3 - home_win_by_4 - home_win_by_5 - home_win_by_6 - home_win_by_7 - home_win_by_8), 3)
            away_odds = round((1 - home_win_by_8) / (1 - (1 / moneyline.odds_home) + home_win_by_1 + home_win_by_2 +
                                    home_win_by_3 + home_win_by_4 + home_win_by_5 + home_win_by_6 + home_win_by_7), 3)
            list_of_handicaps.append(BookmakerHandicap(-8.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass


        # calculate +1, +2, +3 ... +8 lines
        try:
            away_win_by_1 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][1] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][7] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_1) / ((1 / moneyline.odds_away) - away_win_by_1), 3)
            home_odds = round((1 - away_win_by_1) / (1 - (1 / moneyline.odds_away)), 3)
            list_of_handicaps.append(BookmakerHandicap(1.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_2 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][2] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][6] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_2) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2), 3)
            home_odds = round((1 - away_win_by_2) / (1 - (1 / moneyline.odds_away) + away_win_by_1), 3)
            list_of_handicaps.append(BookmakerHandicap(2.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_3 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][3] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][5] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_3) /
                              ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 - away_win_by_3), 3)
            home_odds = round((1 - away_win_by_3) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2), 3)
            list_of_handicaps.append(BookmakerHandicap(3.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_4 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][4] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][4] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_4) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 -
                                                     away_win_by_3 - away_win_by_4), 3)
            home_odds = round((1 - away_win_by_4) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2 +
                                                     away_win_by_3), 3)
            list_of_handicaps.append(BookmakerHandicap(4.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_5 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][5] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][3] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_5) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 -
                                                     away_win_by_3 - away_win_by_4 - away_win_by_5), 3)
            home_odds = round((1 - away_win_by_5) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2 +
                                                     away_win_by_3 + away_win_by_4), 3)
            list_of_handicaps.append(BookmakerHandicap(5.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_6 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][6] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][2] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_6) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 -
                                                     away_win_by_3 - away_win_by_4 - away_win_by_5 - away_win_by_6), 3)
            home_odds = round((1 - away_win_by_6) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2 +
                                                     away_win_by_3 + away_win_by_4 + away_win_by_5), 3)
            list_of_handicaps.append(BookmakerHandicap(6.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_7 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][7] + \
                            self.__probability_table_goal_draws[0][1] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_7) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 -
                                    away_win_by_3 - away_win_by_4 - away_win_by_5 - away_win_by_6 - away_win_by_7), 3)
            home_odds = round((1 - away_win_by_7) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2 +
                                                    away_win_by_3 + away_win_by_4 + away_win_by_5 + away_win_by_6), 3)
            list_of_handicaps.append(BookmakerHandicap(7.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        try:
            away_win_by_8 = self.__probability_table_goal_draws[0][0] * self.__probability_table_goal_draws[1][8]
            away_odds = round((1 - away_win_by_8) / ((1 / moneyline.odds_away) - away_win_by_1 - away_win_by_2 -
                    away_win_by_3 - away_win_by_4 - away_win_by_5 - away_win_by_6 - away_win_by_7- away_win_by_8), 3)
            home_odds = round((1 - away_win_by_8) / (1 - (1 / moneyline.odds_away) + away_win_by_1 + away_win_by_2 +
                                away_win_by_3 + away_win_by_4 + away_win_by_5 + away_win_by_6 + + away_win_by_7), 3)
            list_of_handicaps.append(BookmakerHandicap(8.0, home_odds, away_odds))
        except (ZeroDivisionError, ValueError):
            pass

        list_of_handicaps = sorted(list_of_handicaps, key=lambda bookmaker_handicap: bookmaker_handicap.line)

        # calculate 0.75, 1.25, 1.75, 2.25 ... lines
        i = 1
        asian_lines = []
        for bt in list_of_handicaps:
            try:
                asian_handicap_line = self.__get_asian_handicap_line(bt, list_of_handicaps[i])
                asian_lines.append(asian_handicap_line)
                i += 1
            except IndexError:
                break
        list_of_handicaps += asian_lines
        list_of_handicaps = sorted(list_of_handicaps, key=lambda bookmaker_handicap: bookmaker_handicap.line)

        # create dict
        dict_handicaps = {}
        for handicap in list_of_handicaps:
            dict_handicaps[handicap.line] = handicap

        return dict_handicaps

    def __get_asian_handicap_line(self, line_1: BookmakerHandicap, line_2: BookmakerHandicap) -> BookmakerHandicap:
        """
        Calculates asian handicap line.

        :param line_1: type BookmakerHandicap #1.
        :param line_2: type BookmakerHandicap #2.
        :return: type BookmakerHandicap.
        """

        line = round((line_1.line + line_2.line) / 2, 2)
        home = round((line_1.odds_home + line_2.odds_home) / 2, 3)
        away = round((line_1.odds_away + line_2.odds_away) / 2, 3)
        return BookmakerHandicap(line, home, away)

    def __get_opposite_handicap_odds(self, probability: float) -> float:
        """
        Calculates opposite odds for handicap line by probability of something.

        :param probability: probability of something.
        :return: opposite odds.
        """
        opposite_probability = round(1.00 - probability, 3)
        opposite_odds = round(1 / opposite_probability, 3)
        return opposite_odds