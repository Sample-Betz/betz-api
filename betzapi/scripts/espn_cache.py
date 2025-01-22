

import copy
import json
import os
from bs4 import BeautifulSoup
import requests

write_to_file = lambda path, data: json.dump(data, open(path, 'w'), indent=4)

# ESPN headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def cache_nba_teams():
    """Fetches and caches NBA roster URLs into a JSON file."""
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams'
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data from ESPN API.")
        return None
    
    response_data = response.json()
    teams = response_data['sports'][0]['leagues'][0]['teams']
    
    data = {}
    for team in teams:
        team_name = team['team']['displayName'].lower()
        roster = team['team']['links'][1]['href']
        data[team_name] = roster
        
    # Ensure the directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, '../cache/espn_rosters.json')
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # write to file
    write_to_file(full_path, data)
    
    return data

def cache_team(team_urls: dict):
    """Takes list of urls and gets player attributes"""
    data = {}
    
    for team_name, team_url in team_urls.items():

        response = requests.get(team_url, headers=headers)
        if response.status_code != 200:
            print("Failed to fetch the team page.")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        athletes = soup.find_all('a', attrs={'data-resource-id': 'AthleteName'})
        
        for athlete in athletes:
            # Player attributes
            player_name = athlete.text.lower()
            player_url = athlete['href']
            player_stats_url = player_url.replace('https://www.espn.com/nba/player', 'https://www.espn.com/nba/player/splits')
            
            data[player_name] = {
                'team': team_name,
                'page': player_url,
                'splits': player_stats_url
            }
            
    # Ensure the directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, '../cache/espn_players.json')
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # write to file
    write_to_file(full_path, data)
    
    return data

def main():
    # Cache 
    team_urls = cache_nba_teams()
    
    player_data = cache_team(team_urls)
    
    
if __name__ == '__main__':
    main()