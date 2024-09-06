import pandas as pd

MATCH_OUTCOMES = './raw/nfl/MatchOutcomes.csv'
NFL_STADIUMS = './raw/nfl/NFLStadiums.csv'
PLAYERSTATS = './raw/nfl/PlayerStats.csv'
TEAMROSTER = './raw/nfl/TeamRoster.csv'

TEST_DATA = './processed/nfl/TestData.csv'
FINAL_DATA = './processed/nfl/FinalData.csv'

MIN_YEAR = 2010
MAX_YEAR = 2022

########### UTILS ############

def determine_winner(row):
    if row['score_home'] > row['score_away']: 
        return 1  
    elif row['score_home'] < row['score_away']: 
        return 0 
    return 0.5 

def rename_file(filename):
    return filename.replace('raw', 'processed')

"""
https://brucey.net/nflab/statistics/qb_rating.html

QBR = 	[ [ ( PC / PA * 100 - 30 ) * 0.05 ] + 
        [ ( YG / PA  - 3 ) * 0.25 ] + 
        [ TD / PA * 100 * 0.2 ] + 
        [ 2.375 - ( IC / PA  * 100 * 0.25 ) ] ] / 6 * 100
"""
def calculate_qbr(row):
    # Data based on the player's previous games (accumulative stats)
    pc = row['pass_completions_accum']
    pa = row['pass_attempts_accum']
    yg = row['pass_yards_accum']
    td = row['pass_touchdowns_accum']
    ic = row['pass_interceptions_accum']
    
    try:
        score1 = max(((pc / pa * 100 - 30) * 0.05), 0)
        score2 = max(((yg / pa - 3) * 0.25), 0)
        score3 = max((td / pa * 100 * 0.2), 0)
        score4 = max((2.375 - (ic / pa * 100 * 0.25)), 0)

        return (score1 + score2 + score3 + score4) / 6 * 100
    except ZeroDivisionError:
        return 0

########### FILTERING DATA ############

def process_match_outcomes(filename=MATCH_OUTCOMES):
    # Load the CSV file
    df = pd.read_csv(filename)

    # Filter rows where the year (schedule_season) is between MIN_YEAR and MAX_YEAR (inclusive)
    df = df[(df['schedule_season'] >= MIN_YEAR) & (df['schedule_season'] <= MAX_YEAR)]
    
    # Filter where the week is not 'Wildcard', 'Division', 'Conference', 'Superbowl'
    df = df[~df['schedule_week'].isin(['Wildcard', 'Division', 'Conference', 'Superbowl'])]

    # Keep the scores temporarily for winner calculation
    df = df[['schedule_season', 'schedule_week', 'team_home', 'team_away', 'score_home', 'score_away', 'stadium']]

    # Apply the determine_winner function to each row and assign the result to the 'winner' column
    df['winner'] = df.apply(determine_winner, axis=1)

    # Remove the score columns after calculating the winner
    filtered_df = df.drop(columns=['score_home', 'score_away'])

    # Rename the columns and save the data
    filtered_df.columns = ['season', 'week', 'home_team', 'away_team', 'stadium_name', 'winner']
    filtered_df.to_csv(rename_file(filename), index=False)

    print("Processed Match Outcomes")
    
def process_nfl_stadiums(filename=NFL_STADIUMS):
    try:
        # Try reading the CSV file with a different encoding
        df = pd.read_csv(filename, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        print("Failed to decode using 'ISO-8859-1', trying 'cp1252' encoding.")
        df = pd.read_csv(filename, encoding='cp1252')

    # Select the required columns and rename them
    filtered_df = df[['stadium_name', 'stadium_type', 'stadium_surface']]
    filtered_df.columns = ['stadium_name', 'stadium_type', 'stadium_surface']

    filtered_df.to_csv(rename_file(filename), index=False)
    print("Processed NFL Stadiums")
    
def process_player_stats(filename=PLAYERSTATS):
    # Load the CSV file
    df = pd.read_csv(filename)
    
    # Filter rows where the year (schedule_season) is between MIN_YEAR and MAX_YEAR (inclusive)
    df = df[(df['season'] >= MIN_YEAR) & (df['season'] <= MAX_YEAR)]
    
    # Create a team column 
    df['team'] = df['tm_market'] + " " + df['tm_name']
    
    # Sort the table by season, player, and week
    df = df.sort_values(by=['player', 'season', 'week'])
    
    # Define columns to aggregate  
    metric_renames = {
        'pass_att': 'pass_attempts_accum',
        'pass_cmp': 'pass_completions_accum',
        'pass_yds': 'pass_yards_accum',
        'pass_tds': 'pass_touchdowns_accum',
        'pass_int': 'pass_interceptions_accum',
        'rush_yds': 'rushing_yards_accum',
        'rec_yds': 'receiving_yards_accum',
        'tackles_combined': 'combined_tackles_accum',
        'sacks': 'sacks_accum',
        'fumbles': 'fumbles_accum',
    }
    
    # Store the accumulative stats
    for metric in metric_renames.keys():
        df[metric_renames[metric]] = df.groupby(['player', 'season'])[metric].transform(lambda x: x.shift(1).cumsum().fillna(0))
    
    # Columns to keep and their new names
    column_renames = {
        'season': 'season',
        'week': 'week',
        'team': 'team',
        'player': 'player',
        'pass_att': 'pass_attempts',
        'pass_cmp': 'pass_completions',
        'pass_yds': 'pass_yards',
        'pass_tds': 'pass_touchdowns',
        'pass_int': 'pass_interceptions',
        'rush_yds': 'rushing_yards',
        'rec_yds': 'receiving_yards',
        'tackles_combined': 'combined_tackles',
        'sacks': 'sacks',
        'fumbles': 'fumbles',
    }
    
    # Filter columns and rename them
    columns_to_keep = list(column_renames.keys()) + list(metric_renames.values())
    df_filtered = df[columns_to_keep]
    df_filtered = df_filtered.rename(columns=column_renames)
    
    # Sort the table by team
    df_filtered = df_filtered.sort_values(by=['season', 'week', 'team'])
    
    df_filtered.to_csv(rename_file(filename), index=False)
    print("Processed Player Stats")

def process_team_roster(filename=TEAMROSTER):
    # Load the CSV file
    df = pd.read_csv(filename)
    
    # Filter rows where the year (schedule_season) is between MIN_YEAR and MAX_YEAR (inclusive)
    df = df[(df['season'] >= MIN_YEAR) & (df['season'] <= MAX_YEAR)]

    # Select relevant columns ('Team', 'player', 'position')
    df = df[['player', 'position']]

    # Remove duplicates based on 'player' column
    df_unique = df.drop_duplicates(subset=['player'], keep='first')

    df_unique.to_csv(rename_file(filename), index=False)
    print("Processed Team Roster")

####### MERGING DATA ########

def add_position_to_player_stats():
    player_stats = pd.read_csv(rename_file(PLAYERSTATS))
    team_roster = pd.read_csv(rename_file(TEAMROSTER))

    # Merge the two dataframes on the 'player' column
    merged_df = player_stats.merge(team_roster, on='player', how='left')

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(rename_file(PLAYERSTATS), index=False)

    print("Added Position to Player Stats")
    
def add_stadium_to_match_outcomes():
    match_outcomes = pd.read_csv(rename_file(MATCH_OUTCOMES))
    nfl_stadiums = pd.read_csv(rename_file(NFL_STADIUMS))

    # Merge the two dataframes on the 'stadium_name' column
    merged_df = match_outcomes.merge(nfl_stadiums, on='stadium_name', how='left')

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(rename_file(MATCH_OUTCOMES), index=False)

    print("Added Stadium to Match Outcomes")

def build_training_data():
    # Load the processed data
    match_outcomes = pd.read_csv(rename_file(MATCH_OUTCOMES))
    player_stats = pd.read_csv(rename_file(PLAYERSTATS))
    
    # Data set of QBs only, calculate QBR for each player in the game
    player_stats = player_stats[player_stats['position'] == 'QB']
    player_stats['qbr'] = player_stats.apply(calculate_qbr, axis=1)
    
    # Aggregate statistics by team, season, and week
    qbr_stats = player_stats.groupby(['team', 'season', 'week'])['qbr'].sum().reset_index()
    rushing_stats = player_stats.groupby(['team', 'season', 'week'])['rushing_yards_accum'].sum().reset_index()
    fumbles_stats = player_stats.groupby(['team', 'season', 'week'])['fumbles_accum'].sum().reset_index()
    
    # Define merge and rename function
    def merge_and_rename(df, stats_df, team_col, rename):
        df = df.merge(stats_df, how='left', left_on=[team_col, 'season', 'week'], right_on=['team', 'season', 'week'])
        df = df.rename(columns=rename)
        return df
    
    # Merge stats for home and away teams
    match_outcomes = merge_and_rename(match_outcomes, qbr_stats, 'home_team', {'qbr': 'home_team_qbr'})
    match_outcomes = merge_and_rename(match_outcomes, qbr_stats, 'away_team', {'qbr': 'away_team_qbr'})
    match_outcomes = match_outcomes.drop(columns=['team_x', 'team_y'])
    
    match_outcomes = merge_and_rename(match_outcomes, rushing_stats, 'home_team', {'rushing_yards_accum': 'home_team_rushing_yards'})
    match_outcomes = merge_and_rename(match_outcomes, rushing_stats, 'away_team', {'rushing_yards_accum': 'away_team_rushing_yards'})
    match_outcomes = match_outcomes.drop(columns=['team_x', 'team_y'])
    
    match_outcomes = merge_and_rename(match_outcomes, fumbles_stats, 'home_team', {'fumbles_accum': 'home_team_fumbles'})
    match_outcomes = merge_and_rename(match_outcomes, fumbles_stats, 'away_team', {'fumbles_accum': 'away_team_fumbles'})
    match_outcomes = match_outcomes.drop(columns=['team_x', 'team_y'])
    
    # Drop season from dataset
    match_outcomes = match_outcomes.drop(columns=['season'])
    
    # Save the merged dataframe to a new CSV file
    match_outcomes.to_csv(FINAL_DATA, index=False)
    print("Built Training Data")


####### MAIN FUNCTION ########

def main():
    # process_match_outcomes()
    # process_nfl_stadiums()
    # process_player_stats()
    # process_team_roster()
    
    # add_position_to_player_stats()
    # add_stadium_to_match_outcomes()
    
    build_training_data()
    
    return 0
    
if __name__ == '__main__':
    main()