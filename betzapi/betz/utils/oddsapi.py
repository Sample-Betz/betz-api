import datetime
from typing import List, Dict, Optional
import requests
from betz.utils.utils import odds_sport_conversion, player_props, validate_player_name, load_cache
from django.conf import settings

class OddsAPI:
    BASE_URL = 'https://api.the-odds-api.com'
    
    def __init__(self):
        self.api_key = settings.ODDS_API_KEY
        self.espn_player_stats = load_cache('espn_players.json')

    def get_upcoming(self, sport: str, show_1d: bool = False) -> Optional[List[str]]:
        """Fetches game IDs for upcoming games of a specific sport."""
        params = {'api_key': self.api_key}
        
        if show_1d:
            now = datetime.datetime.now()
            tomorrow = now + datetime.timedelta(days=1)
            params['commenceTimeTo'] = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        url = f'{self.BASE_URL}/v4/sports/{odds_sport_conversion[sport]}/events'
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None
        
        data = []
        
        for game in response.json():
            data.append( {
                'id': game['id'],
                'home': game['home_team'],
                'away': game['away_team']
            } )
        
        return data

    def get_props(self, sport: str, prop: str, platforms: List[str], game_data: str, prop_min: int = None) -> Dict[str, Dict[str, str]]:
        """Fetches player props for a specific sport and prop type."""
        params = {
            'api_key': self.api_key,
            'region': 'us',
            'oddsFormat': 'american',
            'markets': player_props[prop],
            'bookmakers': ','.join(platforms),
        }
        
        url = f"{self.BASE_URL}/v4/sports/{odds_sport_conversion[sport]}/events/{game_data['id']}/odds"
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None
        
        data = {}
        for bookmaker in response.json().get('bookmakers', []):
            for market_type in bookmaker.get('markets', []):
                for player in market_type.get('outcomes', []):
                    # Player name
                    player_name = validate_player_name(player['description'].lower())

                    # Determine player's teeam
                    player_team = self.espn_player_stats[player_name]['team']
                    opp_team = game_data['home'].lower() if game_data['home'].lower() != player_team else game_data['away'].lower()
                    
                    # Determine hom enad awsay team
                    if game_data['home'].lower() != player_team:
                        opp_team = game_data['home'].lower()
                        isHome = True
                    else:
                        opp_team = game_data['away'].lower()
                        isHome = True
                    
                    # Player prop (ex. 1.5)
                    prop_point = player.get('point', 'N/A')
                    
                    # Enforce minimum prop (ex. all greater than 0.5)
                    if prop_min and prop_point > prop_min:
                        data[player_name] = {
                            'team': player_team,
                            'opp': opp_team,
                            'isHomeGame': isHome,
                            'prop': prop_point,
                        }
        return data

