class BookmakerTotal:
    """
    Describes a bookmaker total.

    :var line: line of total.
    :var odds_over: odds for Over.
    :var odds_under: odds for Under.
    """

    def __init__(self, line: float, odds_over: float, odds_under: float):
        self.__line = line
        self.__odds_over = odds_over
        self.__odds_under = odds_under

    @property
    def line(self) -> float:
        return self.__line
    @property
    def odds_over(self) -> float:
        return self.__odds_over
    @property
    def odds_under(self) -> float:
        return self.__odds_under

    def __str__(self):
        return 'Over/Under {}: {} / {}'.format(self.__line, self.__odds_over, self.__odds_under)