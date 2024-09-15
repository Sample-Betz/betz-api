import requests
from bs4 import BeautifulSoup
# from django.conf import settings

from utils import espn_sport_conversion, odds_sport_conversion, market

##### CONSTANTS #####

ESPN_ENDPOINT = 'https://www.espn.com'
ESPN_API_ENDPOINT = 'https://site.api.espn.com'
ODDS_ENDPOINT = 'https://api.the-odds-api.com'

# ODDS_API_KEY = settings.ODDS_API 
ODDS_API_KEY = 'acfb03ce9acfe3c4698d23432a6f7463'

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
    
    # FIX 
    url = f'{ESPN_ENDPOINT}/nfl/game/_/gameId/{game_id}'
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
    
    url = f'{ESPN_API_ENDPOINT}/apis/site/v2/sports/{espn_sport_conversion[sport]}/scoreboard'
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


##### ODDS API #####

def get_odds(sport: str, mkt: str, platform: 'list[str]') -> dict:
    
    params = {
        'api_key': ODDS_API_KEY,
        'region': 'us',
        'oddsFormat': 'american',
        'market': market[mkt],
        'bookmakers': (',').join(platform)
    }
    
    # example
    # https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?api_key=acfb03ce9acfe3c4698d23432a6f7463&region=us&oddsFormat=american&market=h2h&bookmakers=fliff
    
    url = f'{ODDS_ENDPOINT}/v4/sports/{odds_sport_conversion[sport]}/odds/'
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    
    data = {}
    response_data = response.json()
    
    # loop through upcoming games
    for game in response_data:
        home_team = game['home_team']
        away_team = game['away_team']
        espn_name = f'{away_team} at {home_team}' # ESPN formatted name
        
        # initialize the data
        data[espn_name] = {}
        data[espn_name]['home_team'] = home_team
        data[espn_name]['away_team'] = away_team
        
        # loop through each bookmarker or platform (e.g. fliff)
        bookmakers = game['bookmakers']
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker['key']
            
            # intialize bookmaker data
            data[espn_name][bookmaker_name] = {}
            
            # loop through each market (e.g. h2h)
            bookmaker_markets = bookmaker['markets']
            for bookmaker_market in bookmaker_markets:
                market_name = bookmaker_market['key']
                
                outcomes = {}
                for outcome in bookmaker_market['outcomes']:
                    outcome_name = outcome['name']
                    outcome_odds = outcome['price']
                    
                    outcomes[outcome_name] = outcome_odds
                    
                data[espn_name][bookmaker_name][market_name] = outcomes
                
    return data
                
data = get_odds('nfl', 'moneyline', ['fliff']) 
print(data)

""" 
{
    'name': {
        'home_team': 'team',
        'away_team': 'team',
        'bookmaker': [
            {
                'platform': platform,
                'market': [
                    {
                        'type': 'market',
                        'odd1': 'odd1',
                        'odd2': 'odd2',
                    },
                    {
                        'type': 'market',
                        'odd1': 'odd1',
                        'odd2': 'odd2',
                    }
                ]
            },
            {
                'platform': platform,
                'market': [
                    {
                        'type': 'market',
                        'odd1': 'odd1',
                        'odd2': 'odd2',
                    },
                    {
                        'type': 'market',
                        'odd1': 'odd1',
                        'odd2': 'odd2',
                    }
                ]
            }
        ]
    }   
}

{
  'New York Jets at San Francisco 49ers': {
    'home_team': 'San Francisco 49ers',
    'away_team': 'New York Jets',
    'fliff': {
      'h2h': {
        'New York Jets': 160,
        'San Francisco 49ers': -230
      }
    }
  },
  'Buffalo Bills at Miami Dolphins': {
    'home_team': 'Miami Dolphins',
    'away_team': 'Buffalo Bills',
    'fliff': {
      'h2h': {
        'Buffalo Bills': 100,
        'Miami Dolphins': -130
      }
    }
  },
  'Indianapolis Colts at Green Bay Packers': {
    'home_team': 'Green Bay Packers',
    'away_team': 'Indianapolis Colts',
    'fliff': {
      'h2h': {
        'Green Bay Packers': 140,
        'Indianapolis Colts': -195
      }
    }
  },
  'Las Vegas Raiders at Baltimore Ravens': {
    'home_team': 'Baltimore Ravens',
    'away_team': 'Las Vegas Raiders',
    'fliff': {
      'h2h': {
        'Baltimore Ravens': -530,
        'Las Vegas Raiders': 335
      }
    }
  },
  'Los Angeles Chargers at Carolina Panthers': {
    'home_team': 'Carolina Panthers',
    'away_team': 'Los Angeles Chargers',
    'fliff': {
      'h2h': {
        'Carolina Panthers': 210,
        'Los Angeles Chargers': -305
      }
    }
  },
  'Cleveland Browns at Jacksonville Jaguars': {
    'home_team': 'Jacksonville Jaguars',
    'away_team': 'Cleveland Browns',
    'fliff': {
      'h2h': {
        'Cleveland Browns': 155,
        'Jacksonville Jaguars': -195
      }
    }
  },
  'New Orleans Saints at Dallas Cowboys': {
    'home_team': 'Dallas Cowboys',
    'away_team': 'New Orleans Saints',
    'fliff': {
      'h2h': {
        'Dallas Cowboys': -335,
        'New Orleans Saints': 230
      }
    }
  },
  'Tampa Bay Buccaneers at Detroit Lions': {
    'home_team': 'Detroit Lions',
    'away_team': 'Tampa Bay Buccaneers',
    'fliff': {
      'h2h': {
        'Detroit Lions': -325,
        'Tampa Bay Buccaneers': 255
      }
    }
  },
  'San Francisco 49ers at Minnesota Vikings': {
    'home_team': 'Minnesota Vikings',
    'away_team': 'San Francisco 49ers',
    'fliff': {
      'h2h': {
        'Minnesota Vikings': 185,
        'San Francisco 49ers': -255
      }
    }
  },
  'Seattle Seahawks at New England Patriots': {
    'home_team': 'New England Patriots',
    'away_team': 'Seattle Seahawks',
    'fliff': {
      'h2h': {
        'New England Patriots': 140,
        'Seattle Seahawks': -190
      }
    }
  },
  'New York Giants at Washington Commanders': {
    'home_team': 'Washington Commanders',
    'away_team': 'New York Giants',
    'fliff': {
      'h2h': {
        'New York Giants': 120,
        'Washington Commanders': -145
      }
    }
  },
  'New York Jets at Tennessee Titans': {
    'home_team': 'Tennessee Titans',
    'away_team': 'New York Jets'
  },
  'Los Angeles Rams at Arizona Cardinals': {
    'home_team': 'Arizona Cardinals',
    'away_team': 'Los Angeles Rams',
    'fliff': {
      'h2h': {
        'Arizona Cardinals': -125,
        'Los Angeles Rams': -115
      }
    }
  },
  'Cincinnati Bengals at Kansas City Chiefs': {
    'home_team': 'Kansas City Chiefs',
    'away_team': 'Cincinnati Bengals',
    'fliff': {
      'h2h': {
        'Cincinnati Bengals': 195,
        'Kansas City Chiefs': -270
      }
    }
  },
  'Pittsburgh Steelers at Denver Broncos': {
    'home_team': 'Denver Broncos',
    'away_team': 'Pittsburgh Steelers',
    'fliff': {
      'h2h': {
        'Denver Broncos': 140,
        'Pittsburgh Steelers': -175
      }
    }
  },
  'Chicago Bears at Houston Texans': {
    'home_team': 'Houston Texans',
    'away_team': 'Chicago Bears',
    'fliff': {
      'h2h': {
        'Chicago Bears': 230,
        'Houston Texans': -330
      }
    }
  },
  'Atlanta Falcons at Philadelphia Eagles': {
    'home_team': 'Philadelphia Eagles',
    'away_team': 'Atlanta Falcons'
  }
}
"""