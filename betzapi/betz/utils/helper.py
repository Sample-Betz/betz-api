from betz.utils.oddsapi import OddsAPI
from betz.utils.espn import PlayerStats
from betz.utils.fanduel import FanDuelScraper
from betz.utils.statmuse import StatMuseFetcher

from django.core.cache import cache

def odds_api(prop_type: str):
    """Fetch props data from OddsAPI for a given prop type."""
    # Initialize the OddsAPI with your API key
    odds_api = OddsAPI()
    
    # Fetch upcoming NBA games
    games_data = odds_api.get_upcoming('nba', True)

    props = []
    for game_data in games_data:
        # Get props for each game
        game_props = odds_api.get_props('nba', prop_type, ['fliff'], game_data, 0.5)
        if game_props:
            props.append(game_props)
    
    return props

def fanduel():
    """Retrieve NBA team defensive data from FanDuel, using cache for efficiency."""
    # Check if FanDuel defensive data is cached
    cached_data = cache.get('fanduel_defensive_data')
    
    if not cached_data:
        # Fetch and cache data if not available
        scraper = FanDuelScraper()
        defensive_data = scraper.get_fanduel_data(['3pm'])
        cache.set('fanduel_defensive_data', defensive_data, timeout=3600)  # Cache for 1 hour
        return defensive_data
    
    return cached_data

def espn(player: str):
    """Fetch a player's stats from ESPN."""
    player_stats = PlayerStats()
    return player_stats.get_player_stats(player, ['min', '3p%', '3pt_made', '3pt_attempted'])

def statmus(query_type: str, query_param: str):
    """Fetch a prop and get the stats from StatMuse."""
    stat_muse_fetcher = StatMuseFetcher()
    return stat_muse_fetcher.get_stat(query_type, query_param)