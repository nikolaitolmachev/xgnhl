import asyncio

import requests
from Services import scraper, consts
from Entities.nhl_match import NHLMatch
from Poisson.team_quality import TeamQuality
from Poisson.poisson import Poisson
from Poisson.value import Value
from requests_html import AsyncHTMLSession


def analyze_all_matches(PROXY='no') -> None:
    """
    Analyzes all available NHL matches.

    :param PROXY: use proxy to get xG data or no.
    """

    print('=' * 100)

    # get all matches
    # get xG data for all teams at home
    # get xG data for all teams in away
    asession = AsyncHTMLSession()
    loop = asyncio.get_event_loop()
    futures = [
       loop.create_task(scraper.Scraper.get_urls_of_all_matches(asession)),
       loop.create_task(scraper.Scraper.get_xg_data_for_all_teams(asession, PROXY=PROXY)),
       loop.create_task(scraper.Scraper.get_xg_data_for_all_teams(asession, side='away', PROXY=PROXY)),
    ]

    try:
        results = loop.run_until_complete(asyncio.gather(*futures))
        all_links_matches = results[0]
        xg_all_home = results[1]
        xg_all_away = results[2]

        # if xG data web site bannes bot
        if xg_all_home == None and xg_all_away == None:
            return
        else:
            if len(all_links_matches) > 0:
                how_many_matches = '1 match was' if len(all_links_matches) == 1 else f'{len(all_links_matches)} matches were'
                print(f'Succesfull, {how_many_matches} founded.')
                print('=' * 100)

                # analyze every match by URL
                for link in all_links_matches:
                    analyze_single_match(betexplorer_url=link,
                                         XG_ALL_HOME=xg_all_home,
                                         XG_ALL_AWAY=xg_all_away)
                    print('=' * 100)
            else:
                print(consts.ERROR_NO_UPCOMING_MATCHES_ALL)
    except requests.exceptions.ConnectionError:
        print(consts.EXCEPTION_WITH_SCRAPING_WEB_PAGE)


def analyze_single_match(betexplorer_url: str, XG_ALL_HOME=None, XG_ALL_AWAY=None, PROXY='no') -> None:
    """
    Analyzes a single NHL match.

    :param betexplorer_url: betexplorer url of a match which need to analyze.
    :param XG_ALL_HOME: xG data for all home teams. Dict {team_name : (xGF, xGA) }.
    :param XG_ALL_AWAY: xG data for all home teams. Dict {team_name : (xGF, xGA) }.
    :param PROXY: use proxy to get xG data or no.
    """

    print('Scanning...')

    nhl_match = scraper.Scraper.get_main_data_for_nhl_match(
        url=betexplorer_url,
        XG_ALL_HOME=XG_ALL_HOME,
        XG_ALL_AWAY=XG_ALL_AWAY,
        PROXY=PROXY
    )

    if nhl_match != None:
        # if there is some odds (or moneyline, or handicaps, or totals) then work
        # otherwise no sense
        if (nhl_match.bookmaker_moneyline != None or len(nhl_match.bookmaker_handicaps) > 0
                or len(nhl_match.bookmaker_totals)  > 0):
            print(nhl_match)
            # if there are xG data for both teams then work
            # otherwise no sense
            if (nhl_match.team_a.xGF > 0.0 and nhl_match.team_a.xGA > 0.0
                    and nhl_match.team_b.xGA > 0.0 and nhl_match.team_b.xGF > 0.0):
                print(nhl_match.url)

                print('Calculating...')

                # calculate quality of both teams
                quality_home = TeamQuality.calculate(nhl_match.team_a.xGF, nhl_match.team_b.xGA)
                quality_away = TeamQuality.calculate(nhl_match.team_b.xGF, nhl_match.team_a.xGA)
                print(f'Team quality: {quality_home} - {quality_away}')

                # calculate line/odds by user model (Poisson) by team qualities
                poisson = Poisson(quality_home, quality_away)
                # looking for a value
                Value.looking_for_value_by_Poisson(nhl_match, poisson)
            else:
                if nhl_match.team_a.xGF == 0.0 and nhl_match.team_a.xGA == 0.0:
                    print(consts.ERROR_NO_XG_DATA_FOR_HOME)
                if nhl_match.team_b.xGA == 0.0 and nhl_match.team_b.xGF == 0.0:
                    print(consts.ERROR_NO_XG_DATA_FOR_AWAY)
        else:
            print(nhl_match)
            print(consts.ERROR_NO_ANY_LINES_ODDS_FOR_MATCH)


def main() -> None:
    """
    Main function of application.
    """
    print("Welcome to xGNHL application!")

    while True:
        print("=" * 100)
        proxy = input('Do you want to use proxy to get xG data? Y/N: ')
        if proxy.lower() == 'y':
            proxy = 'yes'
            break
        elif proxy.lower() == 'n':
            proxy = 'no'
            break

    while True:
        print("=" * 100)
        print("""Choose the next:        
            1 - To analyze all upcoming matches.                          
            2 - To analyze a single match by a URL.
            or another symbol to exit.""")

        choice = input("Your choice = ")

        if choice == '1':
            analyze_all_matches(PROXY=proxy)

        elif choice == '2':
            print('=' * 100)
            betexplorer_url = input("Write a URL of match: ")
            print('=' * 100)
            # check that url is correct
            if consts.BETEXPLORER_NHL_LEAGUE in betexplorer_url:
                analyze_single_match(betexplorer_url, PROXY=proxy)
            else:
                print(consts.ERROR_WRONG_URL)

        else:
            print("Bye Bye!")
            break


if __name__ == '__main__':
    main()
