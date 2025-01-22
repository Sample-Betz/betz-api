from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from betzapi.betz.scrape.utils import error

##### HELPERS #####

kelly_criterion = lambda win_percentage, decimal_odds: (decimal_odds * win_percentage - (1 - win_percentage)) / decimal_odds

##### API #####

@csrf_exempt
def moneyline(request: HttpRequest):
    # Ensure the request method is GET
    if request.method != 'GET':
        return HttpResponse(status=400)
        
    # Parse the incoming JSON data from the request body
    try:
        query_params = request.GET.dict()
        game_id = query_params['game_id']
        home_odds = float(query_params['home_odds']) / 100
        away_odds = float(query_params['away_odds']) / 100
    except (KeyError, ValueError) as e:
        return error(f"Invalid input: {e}", 400)
    
    # Calculate the win percentages for both teams
    # wp_home, wp_away = win_percentage(game_id)
    api_response = espn_win_percentage(game_id)
    if 'error' in api_response:
        return error(api_response, 400)
    wp_home, wp_away = api_response
    
    # Apply the Kelly Criterion for both teams
    kc_home = kelly_criterion(wp_home, home_odds)
    kc_away = kelly_criterion(wp_away, away_odds)
    
    # Return a JSON response with the calculated values
    return JsonResponse({
        'home': {
            'win_percentage': wp_home,
            'kelly_criterion': kc_home
        },
        'away': {
            'win_percentage': wp_away,
            'kelly_criterion': kc_away
        }
    })