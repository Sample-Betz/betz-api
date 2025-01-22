import logging
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from betz.utils.espn import PlayerStats
from betz.utils.fanduel import FanDuelScraper
from betz.utils.oddsapi import OddsAPI
from betz.utils.openai import PredictionModel
from betz.utils.statmuse import StatMuseFetcher

logger = logging.getLogger(__name__)

##### HELPERS #####

##### API #####

@csrf_exempt
def hello_world(request: HttpRequest):
    # Ensure the request method is GET
    if request.method != 'GET':
        return HttpResponse(status=400)
    
    # Return a JSON response 
    return JsonResponse({
        'message': 'Hello back to you :)'
    }, status=200)