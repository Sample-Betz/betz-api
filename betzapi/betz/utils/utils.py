import json
import os

##### CONVERSION #####

espn_sport_conversion = {
    'nfl': 'football/nfl',
    'nba': 'basketball/nba',
    'nhl': 'hockey/nhl',
    'mlb': 'baseball/mlb'
}

odds_sport_conversion = {
    'nfl': 'americanfootball_nfl',
    'nba': 'basketball_nba',
    'nhl': 'icehockey_nhl',
    'mlb': 'baseball_mlb'
}

market = {
    'spreads': 'spreads',
    'totals': 'totals',
    'moneyline': 'h2h',
    'outrights': 'outrights'
}

player_props = {
    'pts': 'player_points',
    '3ptrs': 'player_threes',
}

odds_api_to_espn = {
    'c.j. mccollum': 'cj mccollum',
    'herb jones': 'herbert jones',
    'b.j. boston jr': 'brandon boston',
    'alex sarr': 'alexandre sarr',
    'pj washington': 'p.j. washington'
}

##### UTILS #####
def load_cache(filename: str) -> dict:
    """Loads a JSON file and returns its contents as a dictionary."""
    try:
        current_dir = os.path.dirname(__file__) 
        cache_dir = os.path.abspath(os.path.join(current_dir, '../../cache'))
        full_path = os.path.join(cache_dir, filename)
        
        with open(full_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' is not valid JSON.")
        return {}

def validate_player_name(player_name: str):
    
    # straight conversion
    if player_name in odds_api_to_espn:
        return odds_api_to_espn[player_name]
    
    # other changes
    if '.' in player_name:
        player_name = player_name.replace('.', '')
        
    if ' jr' in player_name and ' jr.' not in player_name:
        player_name += '.'
        
    return player_name
