import configparser, Services.consts as consts

from Entities.nhl_match import NHLMatch
from Poisson.poisson import Poisson

class Value:
    """
    Static class which looking for a value between bookmakers lines/odds and user model lines/odds.
    """

    @staticmethod
    def calculate_difference_between_odds(user_odds: float, bookmaker_odds: float) -> float:
        """
        Calculates a difference between bookmaker odds and odds which was got from user model (for example, Poisson).

        :param user_odds: odds which was got from user model.
        :param bookmaker_odds: bookmaker odds.
        :return: difference between odds.
        """

        result = round((bookmaker_odds / user_odds - 1) * 100, 3)
        return result

    @staticmethod
    def looking_for_value_by_Poisson(nhl_match: NHLMatch, user_model: Poisson) -> None:
        """
        Compares bookmaker lines/odds with Poisson's model lines/odds and shows and write to stats a value if there is.

        :param nhl_match: type of NHLMatch for which need try to find a value.
        :param user_model: user model, for example, type of Poisson.
        """

        try:
            # get a threshold of value
            config = configparser.ConfigParser()
            config.read('settings.ini')
            MODEL_VALUE_DIFFERENCE = int(config['COMMON']['MODEL_VALUE_DIFFERENCE'])
        except KeyError:
            print(consts.EXCEPTION_SETTINGS_ERROR)
            return

        # info about teams quality
        message_for_stat_quality = f'Team quality: {user_model.home} - {user_model.away}' + '\n'
        message_for_stat = ''
        was_value_ml, was_value_handi, was_value_total = False, False, False

        # get Poisson lines/odds
        poisson_moneyline = user_model.calculate_moneyline_by_Poisson()

        # find a value for bookmaker moneyline
        print('Looking for a value for moneyline...')
        if nhl_match.bookmaker_moneyline == None:
            print('There is no odds for moneyline from bookmaker.')
        else:
            diff_home_win = Value.calculate_difference_between_odds(poisson_moneyline.odds_home, nhl_match.bookmaker_moneyline.odds_home)
            diff_draw = Value.calculate_difference_between_odds(poisson_moneyline.odds_draw, nhl_match.bookmaker_moneyline.odds_draw)
            diff_away_win = Value.calculate_difference_between_odds(poisson_moneyline.odds_away, nhl_match.bookmaker_moneyline.odds_away)
            if diff_home_win >= MODEL_VALUE_DIFFERENCE or diff_draw >= MODEL_VALUE_DIFFERENCE or diff_away_win >= MODEL_VALUE_DIFFERENCE:
                was_value_ml = True
                value_message = '*****There is probably the value!*****'
                print(value_message)
            diff_moneyline_str = f'{nhl_match.bookmaker_moneyline} || Poisson: {poisson_moneyline} \t=> Value = ({diff_home_win} %) - ({diff_draw} %) - ({diff_away_win} %)'
            print(diff_moneyline_str)
            if was_value_ml == True:
                message_for_stat += diff_moneyline_str + '\n'


        # find a value for bookmaker handicaps
        print('Looking for a value for handicaps...')
        if len(nhl_match.bookmaker_handicaps) <= 0:
            print('There are no any handicaps from bookmaker.')
        else:
            # get Poisson handicaps
            poisson_handicaps = user_model.calculate_handicap_odds_by_Poisson(poisson_moneyline)
            # get all available bookmaker handicaps and compare each others with corresponding Poisson
            for bookmaker_handicap in nhl_match.bookmaker_handicaps:
                current_poisson_handicap = poisson_handicaps.get(bookmaker_handicap.line)
                if current_poisson_handicap == None:
                    continue
                else:
                    diff_home_odds = Value.calculate_difference_between_odds(current_poisson_handicap.odds_home, bookmaker_handicap.odds_home)
                    diff_away_odds = Value.calculate_difference_between_odds(current_poisson_handicap.odds_away, bookmaker_handicap.odds_away)
                    if diff_home_odds >= MODEL_VALUE_DIFFERENCE or diff_away_odds >= MODEL_VALUE_DIFFERENCE:
                        was_value_handi = True
                        value_message = '*****There is probably the value!*****'
                        print(value_message)
                    diff_handicap_str = f'{bookmaker_handicap} \t|| Poisson: {current_poisson_handicap.odds_home} / {current_poisson_handicap.odds_away} \t=> Value = {diff_home_odds} % / {diff_away_odds} %'
                    print(diff_handicap_str)
                    if was_value_handi == True:
                        message_for_stat += diff_handicap_str + '\n'
                        was_value_handi = False

        # find a value for bookmaker totals
        print('Looking for a value for totals...')
        if len(nhl_match.bookmaker_totals) <= 0:
            print('There are no any totals from bookmaker.')
        else:
            # get Poisson totals
            poisson_totals = user_model.calculate_total_odds_by_Poisson()
            # get all available bookmaker totals and compare each others with corresponding Poisson
            for bookmaker_total in nhl_match.bookmaker_totals:
                current_poisson_total = poisson_totals.get(bookmaker_total.line)
                if current_poisson_total == None:
                    continue
                else:
                    diff_over_odds = Value.calculate_difference_between_odds(current_poisson_total.odds_over, bookmaker_total.odds_over)
                    diff_under_odds = Value.calculate_difference_between_odds(current_poisson_total.odds_under, bookmaker_total.odds_under)
                    if diff_over_odds >= MODEL_VALUE_DIFFERENCE or diff_under_odds >= MODEL_VALUE_DIFFERENCE:
                        was_value_total = True
                        value_message = '*****There is probably the value!*****'
                        print(value_message)
                    diff_total_str = f'{bookmaker_total} \t|| Poisson: {current_poisson_total.odds_over} / {current_poisson_total.odds_under} \t=> Value = {diff_over_odds} % / {diff_under_odds} %'
                    print(diff_total_str)
                    if was_value_total == True:
                        message_for_stat += diff_total_str + '\n'
                        was_value_total = False

        # write to stats
        if len(message_for_stat) > 0:
            splitting = '=' * 100
            nhl_match.save_to_stats(message_for_stat_quality + message_for_stat + splitting)