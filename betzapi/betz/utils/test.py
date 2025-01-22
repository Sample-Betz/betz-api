from typing import Literal
from pydantic import BaseModel
from openai import OpenAI
from pprint import pprint
from statmuse import StatMuseFetcher
from espn import PlayerStats
from fanduel import FanDuelScraper
from oddsapi import OddsAPI

client = OpenAI(api_key='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')


def odds_api():
    # Initialize the OddsAPI with your API key
    odds_api = OddsAPI(api_key='acfb03ce9acfe3c4698d23432a6f7463')
    
    # Fetch upcoming NBA games
    games_data = odds_api.get_upcoming('nba')

    props = []
    for game_data in games_data:
        game_props = odds_api.get_props('nba', '3ptrs', ['fliff'], game_data)
        if game_props:
            props.append(game_props)
    
    print('## Props')
    pprint(props)
    
    return props

def fanduel():
    scraper = FanDuelScraper()
    return scraper.get_fanduel_data(['3PM'])

def espn(player: str):
    player_stats = PlayerStats()
    return player_stats.get_player_stats(player, ['3P%', '3PT']) 

def statmus(player: str):
    stat_muse_fetcher = StatMuseFetcher()
    return stat_muse_fetcher.get_stat(f'{player} average 3 pointers per game in the last 5 games.')

def predict(player_data):
    # Create the prompt for prediction
    prompt = f'[CONTEXT] Based on the following data about a particular player, make a prediction on the prop. The prop is either over or under that number. The bet is for 3 pointers in his next game based on the data. Use reasoning and any current knowledge on the player you may know. Keep the explanation concise and do not include any special characters or formatting. [DATA] {player_data}'
    
    # Define the Response model with the correct field name
    class Response(BaseModel):
        player_name: str
        prop: str
        result: Literal['over', 'under']
        certainty: float
        explanation: str  # Corrected typo here

    # Make the API call
    completion = client.beta.chat.completions.parse(
        messages=[
            { 'role': 'user', 'content': prompt }
        ],
        model='gpt-4o-2024-08-06',
        response_format=Response
    )
    
    # Print the response message
    response = completion.choices[0].message.parsed
    print(f'Name: {response.player_name}')
    print(f'Prop: {response.prop}')
    print(f'Result: {response.result}')
    print(f'Certainty: {response.certainty}')
    print(f'Explaination: {response.explanation}')

def test():
    
    # props = odds_api()
    
    example_props_data = {
        'tristan da silva': {
            'opp': 'boston celtics',
            'prop': 1.5,
            'team': 'orlando magic'},
        'wendell carter jr.': {
            'opp': 'boston celtics',
            'prop': 0.5,
            'team': 'orlando magic'}}
    
    defensive_data = fanduel()
    
    data = []
    
    for player, props in example_props_data.items():
        # Prop
        prop = props['prop']
        
        # Opp team data
        opp_defensive_data = defensive_data[props['opp']]
        
        # Players stats
        player_stats = espn(player)
        player_last_5g_avg = statmus(player)
        
        compiled_player = {
            'player': player,
            'prop': prop,
            'opp_stats': opp_defensive_data,
            'player_stats': player_stats,
            'L5': player_last_5g_avg
        }
        print(compiled_player)
        
        predict(compiled_player)
    

if __name__ == '__main__':
    test()