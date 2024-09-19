
##### CONVERSIONS #####

team_hrefs = {
    'Arizona Cardinals': 'crd',
    'Atlanta Falcons': 'atl',
    'Baltimore Ravens': 'rav',
    'Buffalo Bills': 'buf',
    'Carolina Panthers': 'car',
    'Chicago Bears': 'chi',
    'Cincinnati Bengals': 'cin',
    'Cleveland Browns': 'cle',
    'Dallas Cowboys': 'dal',
    'Denver Broncos': 'den',
    'Detroit Lions': 'det',
    'Green Bay Packers': 'gnb',
    'Houston Texans': 'htx',
    'Indianapolis Colts': 'clt',
    'Jacksonville Jaguars': 'jax',
    'Kansas City Chiefs': 'kan',
    'Las Vegas Raiders': 'rai',
    'Los Angeles Chargers': 'sdg',
    'Los Angeles Rams': 'ram',
    'Miami Dolphins': 'mia',
    'Minnesota Vikings': 'min',
    'New England Patriots': 'nwe',
    'New Orleans Saints': 'nor',
    'New York Giants': 'nyg',
    'New York Jets': 'nyj',
    'Philadelphia Eagles': 'phi',
    'Pittsburgh Steelers': 'pit',
    'San Francisco 49ers': 'sfo',
    'Seattle Seahawks': 'sea',
    'Tampa Bay Buccaneers': 'tam',
    'Tennessee Titans': 'oti',
    'Washington Commanders': 'was'
}

"""
https://brucey.net/nflab/statistics/qb_rating.html

QBR = 	[ [ ( PC / PA * 100 - 30 ) * 0.05 ] + 
        [ ( YG / PA  - 3 ) * 0.25 ] + 
        [ TD / PA * 100 * 0.2 ] + 
        [ 2.375 - ( IC / PA  * 100 * 0.25 ) ] ] / 6 * 100
"""
def calculate_qbr(pc, pa, yg, td, ic):

    try:
        score1 = max(((pc / pa * 100 - 30) * 0.05), 0)
        score2 = max(((yg / pa - 3) * 0.25), 0)
        score3 = max((td / pa * 100 * 0.2), 0)
        score4 = max((2.375 - (ic / pa * 100 * 0.25)), 0)

        return round((score1 + score2 + score3 + score4) / 6 * 100, 2)
    except ZeroDivisionError:
        return 0