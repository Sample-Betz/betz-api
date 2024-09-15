from django.http import JsonResponse

##### UTILS #####

def error(message: str, code: int):
    return JsonResponse({'error': message}, status=code)


##### CONVERSION #####

espn_sport_conversion = {
    'nfl': 'football/nfl',
    'nba': 'basketball/nba',
    'nhl': 'hockey/nhl',
    'mlb': 'baseball/mlb'
}

odds_sport_conversion = {
    'nfl': 'americanfootball_nfl',
    'nba': 'basketball_nba',
    'nhl': 'icehockey_nhl',
    'mlb': 'baseball_mlb'
}

market = {
    'spreads': 'spreads',
    'totals': 'totals',
    'moneyline': 'h2h',
    'outrights': 'outrights'
}