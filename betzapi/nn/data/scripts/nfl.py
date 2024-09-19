# Standard library imports
import os
import time

# Third-party imports
import pandas as pd
from bs4 import BeautifulSoup

# Local application imports
from custom_logger import get_logger, log_finished
from scraper import Scraper
from utils import team_hrefs, calculate_qbr


class NFLScraper(Scraper):
    def __init__(self, use_proxy: bool = False):
        self.logger = get_logger('NFLScraper')
        
        # Call the parent constructor
        super().__init__(use_proxy, self.logger)
        
        print("#### WELCOME TO NFLSCRAPPER MODULE ####")
    
    # PUBLIC METHODS
    
    def get_team_season(self, team: str, season: int, filename: str = None) -> pd.DataFrame:
        """ Combines gamelog and defense dataframes for a given team and season."""
        time_start = time.time()
        
        # Get gamelog and defense dataframes
        gs_soup = super().scrape(f'https://www.pro-football-reference.com/teams/{team}/{season}/gamelog.htm')
        ads_soup = super().scrape(f'https://www.pro-football-reference.com/teams/{team}/{season}.htm')
        
        # Error with scraping
        if not gs_soup or not ads_soup:
            self.logger.error(f"Failed to scrape {team} {season}")
            return None
        
        general_stats = self.__get_general_stats(gs_soup, team, season)
        advanced_defense_stats = self.__get_advanced_defense(ads_soup, team, season)
        
        if general_stats.empty or advanced_defense_stats.empty:
            self.logger.error(f"Failed to get stats for {team} {season}")
            return None
        
        time_end = time.time()
        
        # Merge the dataframes
        season_df = self.__merge_season_dfs([general_stats, advanced_defense_stats])
        
        # Save to CSV if path is provided
        if filename: 
            self.__df_to_csv(season_df, filename)
            log_finished(self.logger, f"Saved {team} {season} to {filename} in {time_end - time_start:.2f} seconds")
        else:
            log_finished(self.logger, f"Successfully fetched {team} {season} in {time_end - time_start:.2f} seconds")
        
        return season_df
    
    def get_nfl_data(self, start_year: int, end_year: int, path: str = None) -> pd.DataFrame:
        """ Fetches and cleans data for all teams and seasons."""
        dfs = []
        teams = team_hrefs.values()
        
        time_start = time.time()
        
        for year in range(start_year, end_year + 1):
            for team in teams:
                df = self.get_team_season(team, year)
                dfs.append(df)
                
        end_time = time.time()
        
        # Concatenate all dataframes
        final_df = self.__merge_dfs(dfs)
        self.logger.info(f"Successfully fetched data from {start_year} to {end_year}")
        
        # Save to CSV if path is provided
        if path: self.__df_to_csv(final_df, path)
        log_finished(self.logger, f"Saved data from {start_year} to {end_year} to {path} in {end_time - time_start:.2f} seconds")
        
        return final_df
    
    # PRIVATE METHODS
    
    def __get_general_stats(self, soup: BeautifulSoup, team: str, season: int) -> pd.DataFrame:
        """Fetches and cleans a team's gamelog for a given season."""       
        games = self.__clean_table(soup, f'gamelog{season}') 
        data = []
        
        for game in games:
            week = int(game.find('th', {'data-stat': 'week_num'}).text)
            opp = game.find('td', {'data-stat': 'opp'}).text
            is_home = 1 if game.find('td', {'data-stat': 'game_location'}).text == '@' else 0
            is_win = 1 if game.find('td', {'data-stat': 'game_outcome'}).text == 'W' else 0

            passes_completed = self.__get_game_stat(game, 'pass_cmp')
            passes_attempted = self.__get_game_stat(game, 'pass_att')
            passing_yards = self.__get_game_stat(game, 'pass_yds')
            passing_td = self.__get_game_stat(game, 'pass_td')
            passing_int = self.__get_game_stat(game, 'pass_int')
            passing_rating = self.__get_game_stat(game, 'pass_rating', is_float=True)
            rushing_yards_per_attempt = self.__get_game_stat(game, 'rush_yds_per_att', is_float=True)
            
            # Calculate QBR
            qbr = calculate_qbr(passes_completed, passes_attempted, passing_yards, passing_td, passing_int)
            
            # Append the game stats
            data.append([week, team, opp, is_home, is_win, qbr, passing_rating, rushing_yards_per_attempt])
            
        # Create dataframe
        df = pd.DataFrame(data, columns=[
            'Week', 'Team', 'Opponent', 'Is Home', 'Is Win', 'QBR', 'Passing Rating', 'Rushing Yards Per Attempt'
        ])
        
        return df
    
    def __get_advanced_defense(self, soup: BeautifulSoup, team: str, season: int) -> pd.DataFrame:
        """Fetches and cleans a team's defense for a given season."""
        games = self.__clean_table(soup, 'games')
        data = []
        
        for game in games:
            week = int(game.find('th', {'data-stat': 'week_num'}).text)

            defense_pass_yards = self.__get_game_stat(game, 'pass_yds_def')
            defense_rush_yards = self.__get_game_stat(game, 'rush_yds_def')
            defense_turnovers = self.__get_game_stat(game, 'to_def')
            
            data.append([week, defense_pass_yards, defense_rush_yards, defense_turnovers])
            
        df = pd.DataFrame(data, columns=[
            'Week', 'Defense Passing Yards', 'Defense Rushing Yards', 'Defense Turnovers'
        ])
        
        return df
    
    def __clean_table(self, soup: BeautifulSoup, table: str):
        """Cleans the game table by removing playoff, bye week, and canceled games."""
        game_table = soup.find('table', {'id': table})
        games = game_table.find('tbody').find_all('tr')

        # Remove playoff games
        for i, game in enumerate(games):
            game_date = game.find('td', {'data-stat': 'game_date'}).text
            if game_date == 'Playoffs':
                games = games[:i]  # Slice the list to remove playoff games
                break

        # Remove bye weeks and canceled games
        games = [
            game for game in games
            if game.find('td', {'data-stat': 'opp'}).text != 'Bye Week' and 
            game.find('td', {'data-stat': 'boxscore_word'}).text != 'canceled'
        ]
        
        return games
    
    def __get_game_stat(self, game: BeautifulSoup, stat_name: str, is_float=False):
        """Helper function to get game stats and handle empty values."""
        stat = game.find('td', {'data-stat': stat_name}).text
        if stat == '':
            return 0.0 if is_float else 0
        return float(stat) if is_float else int(stat)
    
    def __merge_season_dfs(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """ Merges two dataframes into one."""
        return pd.merge(dfs[0], dfs[1], on='Week')
    
    def __merge_dfs(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """ Merges a list of dataframes into one."""
        return pd.concat(dfs)
    
    def __df_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """ Saves a dataframe to a CSV file."""
        dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(dir)
        nfl_data_dir = os.path.join(parent_dir, 'nfl')
        
        filename = self.__get_unique_filename(nfl_data_dir, filename)
        path = os.path.join(nfl_data_dir, filename)

        df.to_csv(path, index=False)
        
    def __get_unique_filename(self, path: str, filename: str) -> str:
        " Returns a unique filename by appending a number to the end of the filename."
        if not os.path.exists(path):
            os.makedirs(path)
            
        if filename not in os.listdir(path):
            return filename
        
        # Split the filename into name and extension
        name, ext = os.path.splitext(filename)
        counter = 1
        
        # Keep generating new filenames until we find one that doesn't exist
        while os.path.exists(f"{name}_{counter}{ext}"):
            counter += 1
        
        return f"{name}_{counter}{ext}"


def test():
    scraper = NFLScraper(use_proxy=False)
    # scraper.get_team_season('crd', 2020, 'crd_2020.csv')
    # scraper.get_nfl_data(2020, 2020, 'nfl_data.csv')
    
test()