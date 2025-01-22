from bs4 import BeautifulSoup
import requests
from typing import Dict, Optional


class FanDuelScraper:
    BASE_URL = 'https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php'
    RECENCY_MAP = {
        'GC-0 ALL': 'season',
        'GC-7 ALL': 'last 7 games',
        'GC-15 ALL': 'last 15 games',
        'GC-30 ALL': 'last 30 games',
    }

    def __init__(self):
        self.headers = []
        
    def get_fanduel_data(self, filter=None) -> Optional[Dict[str, Dict[str, Dict[str, float]]]]:
        """Fetches and processes FanDuel defense vs position data."""
        soup = self.__fetch_page()
        if not soup:
            return None
        
        self.__extract_headers(soup)
        return self.__extract_data(soup, filter)

    def __fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetches the webpage content and parses it with BeautifulSoup."""
        response = requests.get(self.BASE_URL)
        
        if response.status_code != 200:
            print("Failed to fetch the page.")
            return None
        
        return BeautifulSoup(response.content, 'html.parser')

    def __extract_headers(self, soup: BeautifulSoup) -> None:
        """Extracts table headers from the parsed HTML and stores them."""
        self.headers = [th.get_text(strip=True).lower() for th in soup.find_all('th')]

    def __extract_data(self, soup: BeautifulSoup, filter=None) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Extracts the defense vs position data from the parsed HTML."""
        recency_values = set(self.RECENCY_MAP.keys())
        matching_tr_tags = [
            tr for tr in soup.find_all('tr', class_=True)
            if any(value in " ".join(tr["class"]) for value in recency_values)
        ]

        data = {}
        for tr in matching_tr_tags:
            # Extract team name and abbreviation
            team_cell = tr.find('td', class_='team-cell')
            if not team_cell:
                continue
            
            span_tag = team_cell.find('span')
            team_abbreviation = span_tag.get_text(strip=True) if span_tag else 'N/A'
            team_name = team_cell.get_text(strip=True).replace(team_abbreviation, '').strip().lower()
            
            # Extract numerical values
            values = [float(td.get_text(strip=True)) for td in tr.find_all('td')[1:]]
            team_stats = dict(zip(self.headers[1:], values))
            
            # Store data in the dictionary
            recency_class = " ".join(tr["class"])
            team_data = data.setdefault(team_name, {})
            
            if not filter:
                team_data[self.RECENCY_MAP.get(recency_class, "Unknown")] = team_stats
            else:
                filtered_team_stats = {k: v for k, v in team_stats.items() if k in filter}
                team_data[self.RECENCY_MAP.get(recency_class, "Unknown")] = filtered_team_stats

        return data
