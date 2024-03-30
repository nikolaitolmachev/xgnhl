BETEXPLORER_MAIN = 'https://www.betexplorer.com'
BETEXPLORER_NHL_LEAGUE = 'https://www.betexplorer.com/hockey/usa/nhl/'
BETEXPLORER_SUFFIX_FOR_HANDICAPS = '#ah'
BETEXPLORER_SUFFIX_FOR_TOTALS = '#ou'
XG_SITE_NHL = 'https://www.naturalstattrick.com/teamtable.php?sit=5v5&score=all&rate=y&team=all&loc='

USER_AGENT_SHORT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
USER_AGENT_FULL = 'User-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'

NEEDED_BOOKIES = ('Pinnacle')
MINIMAL_ODDS_TO_GET_LINE = 1.35

FILE_STATS = 'stats.txt'

XG_DIGRESSION_PREFIX = 0.75
XG_DIGRESSION_SUFFIX = 0.05
MAX_SCORE_HOCKEY = 9
SUM_OF_RESULTS_1_X_2 = 3
ALMOST_0 = 0.000001

#possible user errors and application exceptions
ERROR_WRONG_URL = 'Can\'t do anything due to wrong url.'
EXCEPTION_WITH_SCRAPING_WEB_PAGE = 'Can\'t get data from web-page probably due to connection problems.'
ERROR_NO_ANY_LINES_ODDS_FOR_MATCH = 'No sense to do anything due to no any lines/odds.'
ERROR_NO_XG_DATA_FOR_HOME = 'Can\'t get xG data for HOME TEAM probably due to few matches played.'
ERROR_NO_XG_DATA_FOR_AWAY = 'Can\'t get xG data for AWAY TEAM probably due to few matches played.'
ERROR_NO_UPCOMING_MATCHES_ALL = 'Can\'t get anything probably no upcoming matches.'
EXCEPTION_WITH_SCRAPING_XG_PAGE = 'Can\'t get xG data probably due to a ban.'
EXCEPTION_SETTINGS_ERROR = 'Can\'t decode "settings.ini" file.'