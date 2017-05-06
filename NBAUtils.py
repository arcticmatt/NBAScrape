'''
Utility functions for dealing with already saved data.
'''

# Generator for data from a given year (regular season and playoffs)

# Team bucketing type thing? makes 30 folders of 82 files each i.e. each team
# gets a folder with all its data

import json
import os

FILE_DIR = './data/'
TABBREV_INDICES = [18, 25, 32]

TEAMS = set([
    'ATL',
    'BKN',
    'BOS',
    'CHA',
    'CHI',
    'CLE',
    'DAL',
    'DEN',
    'DET',
    'GSW',
    'HOU',
    'IND',
    'LAC',
    'LAL',
    'MEM',
    'MIA',
    'MIL',
    'MIN',
    'NOP',
    'NYK',
    'OKC',
    'ORL',
    'PHI',
    'PHX',
    'POR',
    'SAC',
    'SAS',
    'TOR',
    'UTA',
    'WAS',
])


##### GENERATORS
def data_generator(path):
    '''Creates a generator for the data contained at path.'''

    assert os.path.isdir(path)

    for fname in os.listdir(path):
        if fname[0] == '.': # skip hidden files
            continue
        full_path = os.path.join(path, fname)
        if os.path.isdir(full_path): # skip directories (not recursive)
            continue
        with open(full_path, 'r') as infile:
            data = json.load(infile)
            yield data


def regular_data_generator(year):
    '''Generator for regular season data.'''

    path = os.path.join(FILE_DIR, str(year))

    return data_generator(path)


def team_data_generator(year, teamname):
    '''Generator for a team's data (for a single year).'''

    assert teamname in TEAMS
    path = os.path.join(FILE_DIR, str(year), teamname)
    return data_generator(path)


def playoff_data_generator(year):
    '''Generator for the entire playoffs.'''

    for r in range(1, 5):
        g = playoff_round_data_generator(year, r)
        for data in g:
            yield data


def playoff_round_data_generator(year, p_round):
    '''Generator for a specific round of the playoffs.'''

    assert p_round >= 1 and p_round <= 4
    path = os.path.join(FILE_DIR, str(year), 'Round' + str(p_round))
    return data_generator(path)


##### HELPER FUNCTIONS
def get_teams(data):
    '''Given all rows of data (list of lists), return a list of the two teams involved.'''

    t1 = TABBREV_INDICES[0]
    t2 = TABBREV_INDICES[1]
    t3 = TABBREV_INDICES[2]
    data = [[x[t1], x[t2], x[t3]] for x in data]

    teams = set()
    for a1, a2, a3 in data:
        if a1:
            teams.add(a1)
        if a2:
            teams.add(a2)
        if a3:
            teams.add(a3)
        if len(teams) == 2:
            break

    return list(teams)


def get_gameid(data):
    '''Given all rows of data (list of lists), return a list of the two teams involved.'''

    return str(data[0][0])


##### ORGANIZING DATA
def bucket_by_team(year):
    '''Buckets games by team. The result is 30 folders with 82 files in each.'''

    g = regular_data_generator(year)
    for data in g:
        teams = get_teams(data)
        gameid = get_gameid(data)

        prefix1 = os.path.join(FILE_DIR, str(year), teams[0])
        prefix2 = os.path.join(FILE_DIR, str(year), teams[1])

        if not os.path.exists(prefix1):   # make intermediate dirs, if necessar
            os.makedirs(prefix1)
        if not os.path.exists(prefix2):
            os.makedirs(prefix2)

        fpath1 = os.path.join(prefix1, gameid)
        fpath2 = os.path.join(prefix2, gameid)

        if not os.path.isfile(fpath1):
            with open(fpath1, 'w+') as outfile:
                print 'Saving {} to folder for {}'.format(gameid, teams[0])
                json.dump(data, outfile)
        if not os.path.isfile(fpath2):
            with open(fpath2, 'w+') as outfile:
                print 'Saving {} to folder for {}'.format(gameid, teams[1])
                json.dump(data, outfile)


if __name__ == '__main__':
    bucket_by_team(16)
