import requests

url = 'http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&EndRange=55800&GameID=0041600221&RangeType=2&Season=2016-17&SeasonType=Playoffs&StartPeriod=1&StartRange=0'
base_url = 'http://stats.nba.com/stats/playbyplayv2'
data = { 'EndPeriod': '10', 'EndRange': '55800', 'GameID': '0041600221', 'RangeType': '2', 'Season': '2016-17', 'SeasonType': 'Playoffs', 'StartPeriod': '1', 'StartRange': '0' }
url_test = 'http://stats.nba.com/game/#!/0041600221/playbyplay/'

simpler = 'http://stats.nba.com/stats/playbyplayv2?GameID=0041600221&EndPeriod=10&StartPeriod=1'
new_url = 'http://stats.nba.com/stats/playbyplayv2'
new_data = {'GameID': '0041600221', 'EndPeriod': '10', 'StartPeriod': '1'}


# Get a copy of the default headers that requests would use
# headers = requests.utils.default_headers()

# Update the headers with your custom ones
# You don't have to worry about case-sensitivity with
# the dictionary keys, because default_headers uses a custom
# CaseInsensitiveDict implementation within requests' source code.
# headers.update(
    # {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    # }
# )
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.43 (KHTML, like Gecko) Version/10.0 Safari/602.1.43',
    'referer': 'http://stats.nba.com/scores/',
}
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
    'referer': 'http://stats.nba.com/scores/'
          }

# print 'Getting request...'
# response = requests.get(url, headers=headers, allow_redirects=True)
# response.raise_for_status()
# content = response.text

# try:
    # r = requests.head(url)
    # print(r.status_code)
# except requests.ConnectionError:
    # print("failed to connect")

print requests.get(base_url, params=data, headers=headers, timeout=1)
