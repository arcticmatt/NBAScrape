'''
This script scrapes play-by-play game data from the api used by
http://stats.nba.com/game/#!/GAMEID/playbyplay/
'''

import json
import os
import urlparse
import requests
from NBAUtils import FILE_DIR


START_PERIOD = 1
END_PERIOD = 10
MAX_REGULAR_GAMES = 1230
MAX_PLAYOFF_GAMES = 105
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.43 (KHTML, like Gecko) Version/10.0 Safari/602.1.43',
    'referer': 'http://stats.nba.com/scores/',
}


def create_url(gameid, start_period, end_period):
    '''Creates play-by-play url for the given params.'''

    return 'http://stats.nba.com/stats/playbyplayv2?GameID={gameid}&StartPeriod' \
           '={start_period}&EndPeriod={end_period}'.format(
               gameid=gameid,
               start_period=start_period,
               end_period=end_period,
           )


def parse_url(url):
    '''Returns tuple (base, params) of a url's base and parameters.'''

    parsed = urlparse.urlparse(url)
    base = parsed.scheme + '://' + parsed.netloc + parsed.path
    params = urlparse.parse_qs(parsed.query)
    return (base, params)


def deconstruct_url(url):
    '''
    Deconstructs the gameid of a play-by-play url.

    TODO: remove magic numbers
    '''

    _, params = parse_url(url)
    gameid = params['GameID'][0]
    print 'gameid = {}'.format(gameid)

    if gameid[2] == '2': # regular season url
        year = gameid[3:5]
        game = gameid[6:]
        return (year, game)
    elif gameid[2] == '4':
        year = gameid[3:5]
        p_round = gameid[-3]
        series = gameid[-2]
        game = gameid[-1]
        return (year, p_round, series, game)
    else:
        assert False


def is_valid_url(game_url):
    '''Checks to see if url is valid play-by-play data.'''

    base, params = parse_url(game_url)
    return not (base != 'http://stats.nba.com/stats/playbyplayv2'
         or 'GameID' not in params
         or 'StartPeriod' not in params
         or 'EndPeriod' not in params)


def request_game_data(game_url):
    '''Requests the passed-in url to see if there is data.'''

    base, params = parse_url(game_url)
    response = requests.get(base, params=params, headers=HEADERS, timeout=2)
    response.raise_for_status() # Raise exception if invalid response
    data = response.json()['resultSets'][0]['rowSet']
    return data

def get_game_data(game_url, save=True, prefix=''):
    '''Returns play-by-play data as a list of lists.'''

    if not prefix:
        prefix = FILE_DIR

    assert(is_valid_url(game_url))
    base, params = parse_url(game_url)

    # Check to see if we've saved this data before
    fname = params['GameID'][0]
    print 'Getting game data for GameId = {}'.format(fname)
    fpath = os.path.join(prefix, fname)
    if os.path.isfile(fpath):
        print 'File {} found, loading and returning'.format(fname)
        with open(fpath, 'r') as infile:
            return json.load(infile)

    # Request data
    print 'No file found, sending request'
    data = request_game_data(game_url)
    if not data:
        print 'The url {} points to a nonexistent game. Returning.'.format(game_url)
        return

    # Save data
    if save:
        assert not os.path.isfile(fpath) # we check this above
        if not os.path.exists(prefix):   # make intermediate dirs, if necessar
            os.makedirs(prefix)
        with open(fpath, 'w+') as outfile:
            print 'Saving {} to disk'.format(fname)
            json.dump(data, outfile)

    return data


def create_regular_gameid(year, game_number):
    '''
    Inputs:
    year - the last two digits of the *beginning* year of the season. E.g.
           for the 2015-2016 season, year = 15. For the 1998-1999 season,
           year = 98.
    game_number - the absolute game number of the game in the range [1, 1230] (padded 4 digits)

    Returns:
    The gameid for the desired game as a string.
    '''

    return '002{year}0{game_number:04d}'.format(year=year, game_number=game_number)


def create_playoff_gameid(year, p_round, series, game_number):
    '''
    Inputs:
    year    - the last two digits of the *beginning* year of the season. E.g.
              for the 2015-2016 season, year = 15. For the 1998-1999 season,
              year = 98.
    p_round - the round of the playoffs in the range [1, 4]
    series  - the series number in the range [0, 7] for the first round, [0, 3]
              for the second round, etc.
    game_number - number of games played in the series in the range [1,7]


    Returns:
    The gameid for the desired game as a string.
    '''

    return '004{year}00{p_round}{series}{game_number}'.format(
        year=year, p_round=p_round, series=series, game_number=game_number
    )


def regular_url_generator(year):
    '''
    Inputs:
    year - the last two digits of the *begnning* year of the season.

    Creates a generator for regular season game urls.
    '''

    assert len(str(year)) <= 2

    for game_number in range(1, MAX_REGULAR_GAMES + 1):
    # for game_number in range(1, M):
        gameid = create_regular_gameid(year, game_number)
        url = create_url(gameid, START_PERIOD, END_PERIOD)
        yield url


def playoff_url_generator(year):
    '''
    Inputs:
    year - the last two digits of the *beginning* year of the season.

    Creates a generator for playoff game urls.

    TODO: method that checks if url actually corresponds to a game so we
    can tell when a playoff series has ended
    '''

    assert len(str(year)) <= 2

    num_series = [8, 4, 2, 1]
    # For each round, iterate through each series. For each series, iterate
    # through each game. There is no checking to see whether the url corresponds
    # to an existing game. This checking should be done by the caller of
    # this function.
    for p_round, series in zip(range(1, 5), num_series):
        for s in range(series):
            for game in range(1, 8):
                gameid = create_playoff_gameid(year, p_round, s, game)
                url = create_url(gameid, START_PERIOD, END_PERIOD)
                yield url


def save_regular_season(year):
    '''Saves the passed-in regular season to disk.'''

    assert len(str(year)) <= 2

    g = regular_url_generator(year)
    for url in g:
        get_game_data(url, prefix=os.path.join(FILE_DIR, str(year)))


def save_playoffs(year):
    '''Saves the playoffs to disk, organizing by round.'''

    assert len(str(year)) <= 2

    g = playoff_url_generator(year)
    for url in g:
        _, p_round, _, _ = deconstruct_url(url)
        get_game_data(url, prefix=os.path.join(FILE_DIR, str(year), 'Round' + p_round))


if __name__ == '__main__':
    # save_regular_season(16)
    save_playoffs(15)
