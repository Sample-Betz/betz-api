import logging
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from betz.utils import PredictionModel, espn, statmus, fanduel, odds_api

logger = logging.getLogger(__name__)

##### HELPERS #####
def process_player_data(player, props, defensive_data, model, prop_type):
    """Process data for a single player and predict their performance."""
    # try:
    # Extract prop details
    prop = props['prop']

    # Fetch player stats and recent averages
    player_stats, player_page = espn(player)
    player_last_5g_avg = statmus('3ptrs', player)
    opp_def_rating = statmus('def', props['opp'])

    # Compile player data for prediction
    compiled_player = {
        'player': player,
        'prop': prop,
        'player_stats': player_stats,
        'last_five_games': player_last_5g_avg,
        'opp_stats': defensive_data,
        'opp_def_rating': opp_def_rating
    }

    # Make prediction using the model
    response = model.predict(prop_type, compiled_player)

    # Return structured player data
    return {
        'player': player,
        'espn': player_page,
        'team': props['team'],
        'opp': props['opp'],
        'prop': prop,
        'prediction': {
            'result': response.result,
            'certainty': response.certainty,
            'explanation': response.explanation,
        },
        'stats': {
            'stats': player_stats,
            'last_five_games': player_last_5g_avg,
            'opp_stats': defensive_data,
            'opp_def_rating': opp_def_rating
        }
    }
    # except Exception as e:
    #     # Log errors for debugging
    #     print(f"Error processing player {player}: {e}")
    #     return None

def process_game_props(game_props, defensive_data, model, prop_type):
    """Process props data for all players in a list of games."""
    data = []
    for game in game_props:
        for player, props in game.items():
            # Process data for each player
            logger.warning(f'Processing {player}')
            
            player_data = process_player_data(player, props, defensive_data[props['opp']], model, prop_type)
            if player_data:
                data.append(player_data)
                logger.warning(f'Completed {player}')
            else:
                logger.error(f'Error with {player}')
    return data
    
##### API #####
@csrf_exempt
def player_props(request: HttpRequest):
    # Ensure the request method is GET
    if request.method != 'GET':
        return HttpResponse(status=400)
        
     # Parse the incoming JSON data from the request body
    try:
        query_params = request.GET.dict()
        prop_type = query_params['prop_type']
        match = query_params['match']
    except (KeyError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    # Return data
    data = []
    
    # Get upcoming game props from the bookmakers
    game_props = odds_api(prop_type)
    
    if game_props:
        # Defensive data
        defensive_data = fanduel()
        
        # Predictive model
        model = PredictionModel()

        # Get all props
        data = process_game_props(game_props, defensive_data, model, prop_type)
    
    # Return a JSON response with the calculated values
    return JsonResponse({
        'type': prop_type,
        'data': data,
        'message': 'Success' if data else 'No data found.'
    }, status=200)
    