import requests
from bs4 import BeautifulSoup

# https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b

##### UTILS #####

sport_conversion = {
    'nfl': 'football/nfl',
    'nba': 'basketball/nba',
    'nhl': 'hockey/nhl',
    'mlb': 'baseball/mlb'
}

##### ESPN API #####

def espn_win_percentage(game_id: int) -> tuple | str:
    # ESPN headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    url = f'https://www.espn.com/nfl/game/_/gameId/{game_id}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    # Parse the response
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        home_percent = soup.find('div', class_='matchupPredictor__teamValue--a').text
        away_percent = soup.find('div', class_='matchupPredictor__teamValue--b').text
    except AttributeError:
        return 'Could not parse the response. The game may have already been played.'

    # Convert to float
    home_decimal = float(home_percent.replace('%', '')) / 100
    away_decimal = float(away_percent.replace('%', '')) / 100
    
    return home_decimal, away_decimal

def espn_schedule(sport: str) -> dict:
    
    url = f'https://site.api.espn.com/apis/site/v2/sports/{sport_conversion[sport]}/scoreboard'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    # Initialize the data
    data = {}
    response_data = response.json()
    
    # Parse the response
    upcoming = response_data['events']
    for game in upcoming:
        # Game is completed
        game_status = game['status']['type']['completed']
        if game_status: continue
        
        game_id = game['id']
        game_name = game['name']
        game_url = game['links'][0]['href']
        game_date = game['status']['type']['detail']
        
        data[game_id] = {
            'id': game_id,
            'name': game_name,
            'url': game_url,
            'date': game_date
        }
    
    return data
