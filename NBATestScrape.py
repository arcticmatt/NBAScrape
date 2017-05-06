'''
In this script I will (hopefully) extract game data from this link:
http://stats.nba.com/game/#!/0041600221/playbyplay/

Helpful:
http://stackoverflow.com/questions/30002888/how-to-work-with-data-from-nba-com
http://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
https://github.com/bttmly/nba/issues/21
https://udger.com/resources/ua-list/os-detail?os=macOS%2010.12%20Sierra

Breakdown of data (33 items):
0  - gameId
1  - eventNumber (seems buggy)
2  - NAN
3  - NAN
4  - period
5  - time (est)
6  - periodTimeLeft
7  - homeEvent
8  - NAN
9  - awayEvent
10 - score
11 - NAN
12 - NAN (player something?)
13 - playerId1 (?)
14 - playerName1 (not sure what determines which player)
15 - teamId1
16 - teamLoc1
17 - teamName1
18 - teamAbbrev1
19 - NAN (player something?)
20 - playerId2
21 - playerName2
22 - teamId2
23 - teamLoc2
24 - teamName2
25 - teamAbbrev2
26 - NAN (player something?)
27 - playerId3
28 - playerName3
29 - teamId3
30 - teamLoc3
31 - teamName3
32 - teamAbbrev3
'''

import numpy as np
import matplotlib.pyplot as plt
import json
import os
import urlparse
import time
import requests

FILE_DIR = './data/'
PERIOD_INDEX = 4
PERIOD_TIME_INDEX = 6
SCORE_INDEX = 10
GAMETIME = 48 * 60
OT_LENGTH = 5 * 60

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.43 (KHTML, like Gecko) Version/10.0 Safari/602.1.43',
    'referer': 'http://stats.nba.com/scores/',
}

warriors_url = 'http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&EndRange=55800&GameID=0041600221&RangeType=2&Season=2016-17&SeasonType=Playoffs&StartPeriod=1&StartRange=0'
boston_url = 'http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&EndRange=55800&GameID=0041600202&RangeType=2&Season=2016-17&SeasonType=Playoffs&StartPeriod=1&StartRange=0'


def parse_url(url):
    '''Returns tuple (base, params) of a url's base and parameters.'''

    parsed = urlparse.urlparse(url)
    base = parsed.scheme + '://' + parsed.netloc + parsed.path
    params = urlparse.parse_qs(parsed.query)
    return (base, params)


def get_game_data(game_url, save=True):
    '''Returns play-by-play data as a list of lists.'''

    # Qequest the URL and parse the JSON
    base, params = parse_url(game_url)

    # Check to see if we've saved this data before
    fname = params['GameID'][0]
    print 'Getting game data for GameId = {}'.format(fname)
    fpath = FILE_DIR + fname
    if os.path.isfile(fpath):
        print 'File {} found, loading and returning'.format(fname)
        with open(fpath, 'r') as infile:
            return json.load(infile)

    print 'No file found, sending request'
    response = requests.get(base, params=params, headers=HEADERS, timeout=2)
    response.raise_for_status() # Raise exception if invalid response
    data = response.json()['resultSets'][0]['rowSet']

    # Save data
    if save:
        assert not os.path.isfile(fpath) # we check this above
        with open(fpath, 'w') as outfile:
            print 'Saving {} to disk'.format(fname)
            json.dump(data, outfile)

    return data


def get_score(data_row):
    '''Returns score as a list [teamScore1, teamScore2].'''

    score = data_row[SCORE_INDEX]
    if score:
        return map(int, str(score).replace(' ','').split('-'))
    return None


def get_seconds_elapsed(data_row):
    '''Returns overall seconds elapsed in the game.'''

    period = data_row[PERIOD_INDEX]
    period_time = data_row[PERIOD_TIME_INDEX]
    period_seconds = 12 * 60

    # Time elapsed in current period
    time_struct = time.strptime(str(period_time), '%M:%S')
    seconds_elapsed = period_seconds - (time_struct.tm_min * 60 + time_struct.tm_sec)

    return (period - 1) * period_seconds + seconds_elapsed


def format_game_data(game_url):
    '''
    Formats game data into two lists of (time, score) tuples. Also returns
    the game length (in case of overtime).
    '''

    team1 = [(0, 0)]
    team2 = [(0, 0)]
    last_score1 = 0
    last_score2 = 0
    data = get_game_data(game_url)

    for row in data:
        time_elapsed = get_seconds_elapsed(row)

        score1 = score2 = None
        score = get_score(row)
        if score:
            score1, score2 = get_score(row)

        if score1 and score1 != last_score1:
            assert not (score2 and score2 != last_score2) # teams can't score at same time
            team1.append((time_elapsed, score1))
            last_score1 = score1
        elif score2 and score2 != last_score2:
            team2.append((time_elapsed, score2))
            last_score2 = score2

    max_time = GAMETIME
    max_period = max(map(lambda x: x[PERIOD_INDEX], data))
    max_time = GAMETIME + (max_period - 4) * OT_LENGTH

    return (team1, team2, max_time)


def calculate_average_scores(data, max_time=GAMETIME):
    '''Returns list of average score at each time t.'''

    score_dict = dict(data)
    avg = 0.0
    last_score = 0
    avgs = [] # average over time
    for t in range(max_time):
        t_score = 0
        if t in score_dict:
            t_score = score_dict[t] - last_score
            last_score = t_score
        avg += ((max_time - t) * t_score) / float(max_time)
        avgs.append(avg)

    return avgs


def calculate_average_score(data):
    '''Calculate the average score for the whole game.'''

    return calculate_average_scores(data)[-1]


def calculate_average_score_diffs(data1, data2, reverse=False, max_time=GAMETIME):
    '''
    Given data from format_game_data(), returns the average score difference
    at each time (team1 - team2).
    '''

    if reverse:
        # In this case, we'll calculate the statistic starting at the end of the game.
        data1 = data1[::-1]
        data2 = data2[::-1]

    team_avgs1 = calculate_average_scores(data1, max_time=max_time)
    team_avgs2 = calculate_average_scores(data2, max_time=max_time)

    return np.subtract(team_avgs1, team_avgs2).tolist()


def calculate_average_score_diff(data_tup, reverse=False):
    '''Calculates the average score difference for the game (team1 - team2).'''

    return calculate_average_score_diffs(data_tup, reverse=reverse)[-1]


def plot_time_data(data, title='', max_time=GAMETIME):
    '''Plots the average score diff data against time.'''

    plt.plot(range(max_time), data)
    plt.title(title)
    plt.show()


if __name__ == '__main__':
    data1, data2, max_time = format_game_data(boston_url)
    score_diffs = calculate_average_score_diffs(data1, data2, max_time=max_time)
    plot_time_data(score_diffs, 'Average Score Difference vs. Time', max_time=max_tim   e)
