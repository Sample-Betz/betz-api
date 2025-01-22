import json
import os
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm  # For the loading bar

# ESPN headers
espn_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def load_cache(filename: str) -> dict:
    """Loads a JSON file and returns its contents as a dictionary."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' is not valid JSON.")
        return {}

def espn(gamelog_url: str):
    """Scrapes ESPN for the most recent game data."""
    response = requests.get(gamelog_url, headers=espn_headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr', attrs={'data-idx': ['0', '1', '2']})
    
    if not rows:
        return None
    
    # Get most recent game
    vals = None
    
    for row in rows:
        td_values = [td.text.strip() for td in row.find_all('td', class_='Table__TD')]
        if td_values[0] == 'Fri 12/27':
            vals = td_values
            
    if vals is None:
        return None
    
    columns = [
        'date', 'opp', 'result', 'min', 'fg', 'fg%', '3pt', '3p%', 'ft', 'ft%',
        'reb', 'ast', 'blk', 'stl', 'pf', 'to', 'pts'
    ]
    
    return dict(zip(columns, vals))

def main():
    # Load cached player data
    cached_players = load_cache('/Users/jonahlysne/Developer/SampleBetz/betz-api/betzapi/cache/espn_players.json')
    
    # Example props
    input_file = 'betzapi/examples/v3.json'
    output_file = 'betzapi/results/prop_eval_results.json'
    
    # Load input data
    with open(input_file, 'r') as file:
        json_file = json.load(file)
    
    prop_type = json_file['type']
    results = {
        "Wins": 0,
        "Losses": 0,
        "Players": []
    }
    
    # Process each player prop with a loading bar
    for player_prop in tqdm(json_file['data'], desc="Processing Players", unit="player"):
        player_name = player_prop['player']
        url = cached_players.get(player_name, {}).get('gamelog', None)
        
        if not url:
            print(f"Error: Missing game log URL for {player_name}")
            continue
        
        # Prop details
        prop = float(player_prop['prop'])
        expected_over = player_prop['prediction']['result'] == 'over'
        
        # Fetch game results
        game_data = espn(url)
        if not game_data or '3pt' not in game_data or '-' not in game_data['3pt']:
            print(f"Error: Invalid or missing data for {player_name}")
            continue
        
        threes_made, _ = map(float, game_data['3pt'].split('-'))
        
        # Determine win/loss
        is_win = (
            (expected_over and threes_made > prop) or
            (not expected_over and threes_made < prop)
        )
        
        results["Wins" if is_win else "Losses"] += 1
        results["Players"].append({
            "player": player_name,
            "prop": prop,
            "actual": threes_made,
            "expected": "over" if expected_over else "under",
            "result": "win" if is_win else "loss"
        })
        
    # Save results to JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as outfile:
        json.dump(results, outfile, indent=4)
    
    print(f'PROP EVAL FOR {prop_type}')
    print(f'\tWINS = {results["Wins"]}')
    print(f'\tLOSSES = {results["Losses"]}')
    accuracy = results["Wins"] / (results["Wins"] + results["Losses"]) if (results["Wins"] + results["Losses"]) > 0 else 0
    print(f'\tACCURACY = {accuracy:.2f}')

if __name__ == '__main__':
    main()