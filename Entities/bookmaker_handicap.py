class BookmakerHandicap:
    """
    Describes a bookmaker handicap.

    :var line: line of handicap.
    :var odds_home: odds for home.
    :var odds_away: odds for away.
    """

    def __init__(self, line: float, odds_home: float, odds_away: float):
        self.__line = line
        self.__odds_home = odds_home
        self.__odds_away = odds_away

    @property
    def line(self) -> float:
        return self.__line
    @property
    def odds_home(self) -> float:
        return self.__odds_home
    @property
    def odds_away(self) -> float:
        return self.__odds_away

    def __str__(self):
        return '{}: {} / {}'.format(self.__line, self.__odds_home, self.__odds_away)