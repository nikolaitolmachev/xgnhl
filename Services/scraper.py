import Services.consts as consts, time, asyncio, configparser
import requests.exceptions
from Entities.nhl_match import NHLMatch, Team, BookmakerMoneyline
from Entities.bookmaker_handicap import BookmakerHandicap
from Entities.bookmaker_total import BookmakerTotal

from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from lxml import html

class Scraper:
    """
    Static class to get an information from web-page.
    """

    @staticmethod
    def __get_web_page_requests_html(url: str) -> html.HtmlElement:
        """
        Gets a html of web-page by url using requests_html.

        :param url: url which needs to scrape.
        :return: html tree of page.
        """

        try:
            header = {'User-agent': consts.USER_AGENT_SHORT}
            session = HTMLSession()
            request = session.get(url, headers=header)
            request.html.render()
            return html.fromstring(request.html.html)
        except requests.exceptions.ConnectionError:
            print(consts.EXCEPTION_WITH_SCRAPING_WEB_PAGE + ' - ' + url)

    @staticmethod
    def get_main_data_for_nhl_match(url: str, attempts=1, XG_ALL_HOME=None, XG_ALL_AWAY=None, PROXY='no') -> NHLMatch:
        """
        Gets main data for a single match: KO time, teams and moneyline.

        :param url: betexplorer url of a single match.
        :param attempts: number of trying to get data.
        :param XG_ALL_HOME: xG data for all home teams. Dict {team_name : (xGF, xGA) }
        :param XG_ALL_AWAY: xG data for all home teams. Dict {team_name : (xGF, xGA) }
        :return: type NHLMatch
        """

        nhl_match = None

        try:
            tree = Scraper.__get_web_page_requests_html(url)
            time.sleep(1.5)

            # create a nhl match
            # get a teams
            match_name = tree.xpath('//span[@class="list-breadcrumb__item__in"]/text()')[0]
            team_a = Team(match_name.split(' - ')[0].strip())
            team_b = Team(match_name.split(' - ')[-1].strip())
            # get a date
            match_date = tree.xpath('//p[@class="list-details__item__date"]/text()')[0]

            # get bookmaker moneyline
            bookmaker_moneyline = None
            odds_table = tree.xpath('.//table[@class="table-main h-mb15 sortable"]/tbody/tr[@data-originid="1"]')
            for odds_row in odds_table:
                bookmaker = odds_row.xpath('.//td[@class="h-text-left over-s-only"]/a/text()')[0]
                if bookmaker in consts.NEEDED_BOOKIES:
                    try:
                        home_odds = float(odds_row.xpath('.//td[last()-2]')[0].attrib['data-odd'])
                        draw_odds = float(odds_row.xpath('.//td[last()-1]')[0].attrib['data-odd'])
                        away_odds = float(odds_row.xpath('.//td[last()]')[0].attrib['data-odd'])
                        bookmaker_moneyline = BookmakerMoneyline(home_odds, draw_odds, away_odds)
                    except ValueError:
                        pass

            nhl_match = NHLMatch(match_date, team_a, team_b, url, bookmaker_moneyline)

            if bookmaker_moneyline != None:


                # get list of bookmaker handicaps, bookmaker totals and xG data for both teams
                # modify url to get bookmaker handicaps
                url_handicaps = url
                url_handicaps += consts.BETEXPLORER_SUFFIX_FOR_HANDICAPS if url[-1] == '/' else '/' + consts.BETEXPLORER_SUFFIX_FOR_HANDICAPS

                # modify url to get bookmaker totals
                url_totals = url
                url_totals += consts.BETEXPLORER_SUFFIX_FOR_TOTALS if url[-1] == '/' else '/' + consts.BETEXPLORER_SUFFIX_FOR_TOTALS

                asession = AsyncHTMLSession()
                loop = asyncio.get_event_loop()

                # if xG data has been already got
                if XG_ALL_HOME != None and XG_ALL_AWAY != None:
                    futures = [
                        loop.create_task(Scraper.__get_bookmaker_handicaps(url_handicaps, asession)),
                        loop.create_task(Scraper.__get_bookmaker_totals(url_totals, asession)),
                    ]
                    results = loop.run_until_complete(asyncio.gather(*futures))

                    nhl_match.bookmaker_handicaps = results[0]
                    nhl_match.bookmaker_totals = results[1]

                    # get xG data for home team
                    try:
                        nhl_match.team_a.xGF = XG_ALL_HOME.get(nhl_match.team_a.name.replace('.', ''))[0]
                        nhl_match.team_a.xGA = XG_ALL_HOME.get(nhl_match.team_a.name.replace('.', ''))[1]
                    except TypeError:
                        nhl_match.team_a.xGF = 0.0
                        nhl_match.team_a.xGA = 0.0

                    # get xG data for away team
                    try:
                        nhl_match.team_b.xGF = XG_ALL_AWAY.get(nhl_match.team_b.name.replace('.', ''))[0]
                        nhl_match.team_b.xGA = XG_ALL_AWAY.get(nhl_match.team_b.name.replace('.', ''))[1]
                    except TypeError:
                        nhl_match.team_b.xGF = 0.0
                        nhl_match.team_b.xGA = 0.0

                else:
                    futures = [
                        loop.create_task(Scraper.__get_bookmaker_handicaps(url_handicaps, asession)),
                        loop.create_task(Scraper.__get_bookmaker_totals(url_totals, asession)),
                        loop.create_task(Scraper.__get_xg_data_for_two_teams(consts.XG_SITE_NHL + 'H', asession, nhl_match.team_a.name, PROXY=PROXY)),
                        loop.create_task(Scraper.__get_xg_data_for_two_teams(consts.XG_SITE_NHL + 'A', asession, nhl_match.team_b.name, PROXY=PROXY)),
                    ]
                    results = loop.run_until_complete(asyncio.gather(*futures))

                    nhl_match.bookmaker_handicaps = results[0]
                    nhl_match.bookmaker_totals = results[1]
                    nhl_match.team_a.xGF = results[2][0]
                    nhl_match.team_a.xGA = results[2][1]
                    nhl_match.team_b.xGF = results[3][0]
                    nhl_match.team_b.xGA = results[3][1]

                while len(nhl_match.bookmaker_handicaps) == 0:
                    nhl_match.bookmaker_handicaps = Scraper.__get_bookmaker_handicaps_repeat(url_handicaps)
                while len(nhl_match.bookmaker_totals) == 0:
                    nhl_match.bookmaker_totals = Scraper.__get_bookmaker_totals_repeat(url_totals)

            return nhl_match
        except IndexError:
            if attempts <= 3:
                attempts += 1
                nhl_match = Scraper.get_main_data_for_nhl_match(url, attempts, XG_ALL_HOME, XG_ALL_AWAY)
            return nhl_match
        except AttributeError:
            return nhl_match

    @staticmethod
    async def __get_bookmaker_handicaps(url: str, asession: AsyncHTMLSession) -> list:
        """
        Gets a bookmaker lines and odds of handicap for a single match.

        :param url: url of bookmakers handicaps.
        :param asession: current session.
        :return: list of type BookmakerHandicap.
        """

        def modify_handicap_line(handicap_line: str) -> float:
            """
            Modifies asian handicap line from string to float.

            :param handicap_line: string of handicap line.
            :return: float of handicap line.
            """

            try:
                return float(handicap_line)
            except ValueError:
                asian_handicap = handicap_line.split(',')
                return (float(asian_handicap[0]) + float(asian_handicap[1])) / 2

        list_of_handicaps = []

        header = {'User-agent': consts.USER_AGENT_SHORT}
        request = await asession.get(url, headers=header)
        await request.html.arender()
        tree = html.fromstring(request.html.html)

        # get all lines with odds
        odds_all = tree.xpath('//div[@id="odds-content"]/div[@class="box-overflow"]/div')
        for el in odds_all:
            rows = el.xpath('.//table/tbody/tr')
            handicap_line = rows[0].xpath('.//td[@class="table-main__doubleparameter"]/text()')[0]
            for row in rows:
                bookmaker = row.xpath('.//td[@class="h-text-left over-s-only"]/a/text()')[0]
                if bookmaker in consts.NEEDED_BOOKIES:
                    try:
                        odds_home = float(row.xpath('.//td[last()-1]')[0].attrib['data-odd'])
                        odds_away = float(row.xpath('.//td[last()]')[0].attrib['data-odd'])
                    except ValueError:
                        continue
                    # if odds too low then skip this handicap line
                    if (odds_home < consts.MINIMAL_ODDS_TO_GET_LINE
                            or odds_away < consts.MINIMAL_ODDS_TO_GET_LINE):
                        continue
                    else:
                        handicap_line_to_digit = modify_handicap_line(handicap_line)
                        book_handi = BookmakerHandicap(handicap_line_to_digit, odds_home, odds_away)
                        list_of_handicaps.append(book_handi)
                        break
                else:
                    continue
        return list_of_handicaps

    @staticmethod
    def __get_bookmaker_handicaps_repeat(url: str) -> list:
        """
        Gets a bookmaker lines and odds of handicap for a single match.

        :param url: url of bookmakers handicaps.
        :return: list of type BookmakerHandicap.
        """

        def modify_handicap_line(handicap_line: str) -> float:
            """
            Modifies asian handicap line from string to float.

            :param handicap_line: string of handicap line.
            :return: float of handicap line.
            """

            try:
                return float(handicap_line)
            except ValueError:
                asian_handicap = handicap_line.split(',')
                return (float(asian_handicap[0]) + float(asian_handicap[1])) / 2

        list_of_handicaps = []

        tree = Scraper.__get_web_page_requests_html(url)
        time.sleep(1.5)

        # get all lines with odds
        odds_all = tree.xpath('//div[@id="odds-content"]/div[@class="box-overflow"]/div')
        for el in odds_all:
            rows = el.xpath('.//table/tbody/tr')
            handicap_line = rows[0].xpath('.//td[@class="table-main__doubleparameter"]/text()')[0]
            for row in rows:
                bookmaker = row.xpath('.//td[@class="h-text-left over-s-only"]/a/text()')[0]
                if bookmaker in consts.NEEDED_BOOKIES:
                    try:
                        odds_home = float(row.xpath('.//td[last()-1]')[0].attrib['data-odd'])
                        odds_away = float(row.xpath('.//td[last()]')[0].attrib['data-odd'])
                    except ValueError:
                        continue
                    # if odds too low then skip this handicap line
                    if (odds_home < consts.MINIMAL_ODDS_TO_GET_LINE
                            or odds_away < consts.MINIMAL_ODDS_TO_GET_LINE):
                        continue
                    else:
                        handicap_line_to_digit = modify_handicap_line(handicap_line)
                        book_handi = BookmakerHandicap(handicap_line_to_digit, odds_home, odds_away)
                        list_of_handicaps.append(book_handi)
                        break
                else:
                    continue
        return list_of_handicaps

    @staticmethod
    async def __get_bookmaker_totals(url: str, asession: AsyncHTMLSession) -> list:
        """
        Gets a bookmaker lines and odds of total for a single match.

        :param url: url of bookmakers totals.
        :param asession: current session.
        :return: list of type BookmakerTotal.
        """

        list_of_totals = []

        header = {'User-agent': consts.USER_AGENT_SHORT}
        request = await asession.get(url, headers=header)
        await request.html.arender()
        tree = html.fromstring(request.html.html)

        # get all lines with odds
        odds_all = tree.xpath('//div[@id="odds-content"]/div[@class="box-overflow"]/div')
        for el in odds_all:
            rows = el.xpath('.//table/tbody/tr')
            total_line = float(rows[0].xpath('.//td[@class="table-main__doubleparameter"]/text()')[0])
            for row in rows:
                bookmaker = row.xpath('.//td[@class="h-text-left over-s-only"]/a/text()')[0]
                if bookmaker in consts.NEEDED_BOOKIES:
                    try:
                        odds_home = float(row.xpath('.//td[last()-1]')[0].attrib['data-odd'])
                        odds_away = float(row.xpath('.//td[last()]')[0].attrib['data-odd'])
                    except ValueError:
                        continue
                    # if odds too low then skip this total line
                    if (odds_home < consts.MINIMAL_ODDS_TO_GET_LINE
                            or odds_away < consts.MINIMAL_ODDS_TO_GET_LINE):
                        continue
                    else:
                        book_total = BookmakerTotal(total_line, odds_home, odds_away)
                        list_of_totals.append(book_total)
                        break
                else:
                    continue
        return list_of_totals

    @staticmethod
    def __get_bookmaker_totals_repeat(url: str) -> list:
        """
        Gets a bookmaker lines and odds of total for a single match.

        :param url: url of bookmakers totals.
        :return: list of type BookmakerTotal.
        """

        list_of_totals = []

        tree = Scraper.__get_web_page_requests_html(url)
        time.sleep(1.5)

        # get all lines with odds
        odds_all = tree.xpath('//div[@id="odds-content"]/div[@class="box-overflow"]/div')
        for el in odds_all:
            rows = el.xpath('.//table/tbody/tr')
            total_line = float(rows[0].xpath('.//td[@class="table-main__doubleparameter"]/text()')[0])
            for row in rows:
                bookmaker = row.xpath('.//td[@class="h-text-left over-s-only"]/a/text()')[0]
                if bookmaker in consts.NEEDED_BOOKIES:
                    try:
                        odds_home = float(row.xpath('.//td[last()-1]')[0].attrib['data-odd'])
                        odds_away = float(row.xpath('.//td[last()]')[0].attrib['data-odd'])
                    except ValueError:
                        continue
                    # if odds too low then skip this total line
                    if (odds_home < consts.MINIMAL_ODDS_TO_GET_LINE
                            or odds_away < consts.MINIMAL_ODDS_TO_GET_LINE):
                        continue
                    else:
                        book_total = BookmakerTotal(total_line, odds_home, odds_away)
                        list_of_totals.append(book_total)
                        break
                else:
                    continue
        return list_of_totals

    @staticmethod
    async def __get_xg_data_for_two_teams(url: str, asession: AsyncHTMLSession, team_name: str, PROXY='no') -> tuple:
        """
        Gets xG data (xGF, xGA) for a team.

        :param url: url of xG data.
        :param asession: current session.
        :param team_name: name of team.
        :param PROXY: use proxy to get xG data or no.
        :return: tuple (xGF, xGA).
        """

        xGF, xGA = 0.0, 0.0

        try:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            MINIMAL_MATCHES_TO_COUNT = int(config['COMMON']['MINIMAL_MATCHES_TO_COUNT'])

            # if need to use proxy to get xG data
            if PROXY == 'yes':
                USER_AGENT = config['COMMON']['USER_AGENT']
                header = {'User-agent': USER_AGENT}

                PROXY_ADRRESS = config['COMMON']['PROXY']
                proxy_list = {
                    'https': PROXY_ADRRESS
                }
                asession.proxies.update(proxy_list)
            else:
                header = {'User-agent': consts.USER_AGENT_SHORT}
        except KeyError:
            print(consts.EXCEPTION_SETTINGS_ERROR)
            return

        # get xG data
        try:
            request = await asession.get(url, headers=header)
            #await request.html.arender()
            tree = html.fromstring(request.html.html)

            teams_table = tree.xpath('//table[@id="teams"]/tbody/tr')
            for elem in teams_table:
                team_name_ = elem.xpath('./td[@class="lh"]/text()')[0]
                if team_name.replace('.', '') == team_name_:
                    games_played = int(elem.xpath('./td[3]/text()')[0])
                    if games_played >= MINIMAL_MATCHES_TO_COUNT:
                        xGF = float(elem.xpath('./td[23]/text()')[0])
                        xGA = float(elem.xpath('./td[24]/text()')[0])
                    break
        except requests.exceptions.ConnectionError:
            print(consts.EXCEPTION_WITH_SCRAPING_XG_PAGE)
            xGF, xGA = -1, -1
        finally:
            return (xGF, xGA)

    @staticmethod
    async def get_urls_of_all_matches(asession: AsyncHTMLSession) -> list:
        """
        Gets URL's of all upcoming matches.

        :param asession: current session.
        :return: list of URL's of all upcoming matches.
        """

        header = {'User-agent': consts.USER_AGENT_SHORT}
        request = await asession.get(consts.BETEXPLORER_NHL_LEAGUE, headers=header)
        await request.html.arender()
        tree = html.fromstring(request.html.html)

        urls = []

        # get rows of future matches
        rows = tree.xpath('//div[@class="box-overflow__in"]/table/tbody/tr')
        for row in rows:
            try:
                # get odds
                are_odds = row.xpath('./td[@class="table-main__odds"]/button/text()')
                if len(are_odds) != 0:
                    # get link
                    match_full_link = consts.BETEXPLORER_MAIN + \
                                      row.xpath('./td[2]/a[@class="in-match"]')[0].attrib['href']
                    urls.append(match_full_link)
            except IndexError:
                continue

        return urls

    @staticmethod
    async def get_xg_data_for_all_teams(asession: AsyncHTMLSession, side='home', PROXY='no') -> dict:
        """
        Gets dict {team_name : (xGF, xGA) } with all teams when played at home or away.

        :param asession: current session.
        :param side: depends on venue.
        :param PROXY: use proxy to get xG data or no.
        :return: dict {team_name : (xGF, xGA) }.
        """

        teams = {}

        try:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            MINIMAL_MATCHES_TO_COUNT = int(config['COMMON']['MINIMAL_MATCHES_TO_COUNT'])

            # if need to use proxy to get xG data
            if PROXY == 'yes':
                USER_AGENT = config['COMMON']['USER_AGENT']
                header = {'User-agent': USER_AGENT}

                PROXY_ADRRESS = config['COMMON']['PROXY']
                proxy_list = {
                    'https': PROXY_ADRRESS
                }
                asession.proxies.update(proxy_list)
            else:
                header = {'User-agent': consts.USER_AGENT_SHORT}
        except KeyError:
            print(consts.EXCEPTION_SETTINGS_ERROR)
            return

        # get xG data
        try:
            url = consts.XG_SITE_NHL + 'H' if side == 'home' else consts.XG_SITE_NHL + 'A'
            request = await asession.get(url, headers=header)
            #await request.html.arender()
            tree = html.fromstring(request.html.html)

            teams_table = tree.xpath('//table[@id="teams"]/tbody/tr')
            for elem in teams_table:
                xGF, xGA = 0.0, 0.0
                team_name = elem.xpath('./td[@class="lh"]/text()')[0]
                games_played = int(elem.xpath('./td[3]/text()')[0])
                if games_played >= MINIMAL_MATCHES_TO_COUNT:
                    xGF = float(elem.xpath('./td[23]/text()')[0])
                    xGA = float(elem.xpath('./td[24]/text()')[0])
                    teams[team_name] = (xGF, xGA)
        except requests.exceptions.ConnectionError:
            print(consts.EXCEPTION_WITH_SCRAPING_XG_PAGE)
            teams = None
        finally:
            return teams

