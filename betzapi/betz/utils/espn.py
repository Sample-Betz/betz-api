
from bs4 import BeautifulSoup
import requests
from betz.utils.utils import load_cache

# ESPN headers
espn_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

class PlayerStats:
    TITLES = [
        'gp', 'min', 'fg', 'fg%', '3pt', '3p%', 'ft', 'ft%', 
        'or', 'dr', 'reb', 'ast', 'blk', 'stl', 'pf', 'to', 'pts'
    ]
    
    def __init__(self):
        self.headers = espn_headers
        self.espn_player_stats = load_cache('espn_players.json')

    def get_player_stats(self, player_name: str, filter=None):
        """Fetch and parse player stats."""
        player_attributes = self.espn_player_stats[player_name]
        
        player_page = player_attributes['splits']
        
        html_text = self.__fetch_data(player_page)
        if html_text:
            return (self.__parse_data(html_text, filter), player_attributes['page'])
        return None
    
    def __fetch_data(self, url: str):
        """Fetch the data from the player's URL."""
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print("Failed to fetch player data.")
            return None
        
        return response.text

    def __parse_data(self, html_text: str, filter=None):
        """Parse the HTML response and extract player stats."""
        soup = BeautifulSoup(html_text, 'html.parser')
        rows = soup.find_all('tr', attrs={'data-idx': ['1', '2']})
        
        data = {}
        is_home = True
        
        # Iterate through each row and extract values from inner <td> tags
        for row in rows:
            td_values = [td.text.strip() for td in row.find_all('td', class_='Table__TD')]
            
            # Only grab specific dataset
            if len(td_values) != 17:
                continue
            
            # Map td values to headers
            row_data = dict(zip(self.TITLES, td_values))
            
            # Adjust combined stats
            row_data['fg_made'], row_data['fg_attempted'] = row_data.pop('fg').split('-')
            row_data['3pt_made'], row_data['3pt_attempted'] = row_data.pop('3pt').split('-')
            row_data['ft_made'], row_data['ft_attempted'] = row_data.pop('ft').split('-')
            
            # Optional filter
            if filter: row_data = {k: v for k, v in row_data.items() if k in filter}
            
            # Record if its a home game
            if is_home:
                data['home'] = row_data
                is_home = False
            else:
                data['away'] = row_data
        
        return data
