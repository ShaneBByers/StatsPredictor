import urllib.request
import ssl
from bs4 import BeautifulSoup

# ssl._create_default_https_context = ssl._create_unverified_context
#
# fp = urllib.request.urlopen("http://rotogrinders.com/lineups/nhl?site=fanduel")
# mybytes = fp.read()
#
# mystr = mybytes.decode("utf8")
# fp.close()

text_file = open("testing.txt", "r")

mystr = text_file.read()

soup = BeautifulSoup(mystr, 'html.parser')

ul = soup.find('ul', 'lst lineup')
li_list = ul.find_all('li', attrs={'data-role': 'lineup-card'})

for li in li_list:
    away_team_name = li['data-away']
    home_team_name = li['data-home']
    away_team = li.find('div', 'blk away-team')
    away_lines = away_team.find_all('div', 'blk nhl')
    for away_line in away_lines:
        line_number = away_line.find('h4').string
        line_players = away_line.find_all('div', 'info')
        for line_player in line_players:
            player = line_player.find('a')
            player_id = player['href'][-5:]
            player_name = player['title']
            position = line_player.find('span', 'position').string
            extra = line_player.find('span', 'stats').find('span', 'stats').string
            salary = line_player.find('span', 'salary').string


text_file.close()