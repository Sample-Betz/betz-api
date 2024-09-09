from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from betz.views.utils import error
from betz.views.external import espn_win_percentage, espn_schedule

SPORTS = ['nfl', 'nba', 'nhl', 'mlb']

##### API #####

@csrf_exempt
def win_percentage(request: HttpRequest):
    # Not a GET request
    if request.method != 'GET':
        return error('GET only', 400)
    
    try:
        query_params = request.GET.dict()
        game_id = query_params['game_id']
    except (KeyError, ValueError) as e:
        error(f"Invalid input: {e}", 400)
    
    api_response = espn_win_percentage(game_id)
    if 'error' in api_response:
        return JsonResponse(api_response, status=400)
    wp_home, wp_away = api_response
    
    return JsonResponse({
        'home': { 'win_percentage': wp_home },
        'away': { 'win_percentage': wp_away }
    })
    
@csrf_exempt
def schedule(request: HttpRequest):
    # Not a GET request
    if request.method != 'GET': 
        return error('GET only', 400)
    
    try:
        query_params = request.GET.dict()
        sport = query_params['sport'].lower()
    except (KeyError, ValueError) as e:
        return error(f"Invalid input: {e}", 400)
    
    if sport not in SPORTS: 
        return error('Invalid sport', 400)
    
    data = espn_schedule(sport)
    if not data: return error('ESPN error', 500)
    
    return JsonResponse( data )
