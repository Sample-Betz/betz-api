from bs4 import BeautifulSoup
import requests

prompt_library = {
    'pts': '',
    '3ptrs': lambda player: f'What is the average 3 pointers per game fo r{player} in the last 5 games?',
    'def': lambda team: f'What is the defensive rating for {team} this season?',
}

class StatMuseFetcher:
    BASE_URL = 'https://www.statmuse.com/nba/ask/'
    
    def __init__(self):
        """Initialize with the player's name and stat query."""
        # Eventually store prompt library here
    
    def fetch_data(self, query: str):
        """Fetch the page content from StatMuse."""
        response = requests.get(f'{self.BASE_URL}{query}')
        if response.status_code != 200:
            print("Failed to fetch the page.")
            return None
        return response.content

    def parse_data(self, html_content):
        """Parse the HTML content to extract the stat answer."""
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the specific span containing the answer
        result_span = soup.find('span', class_='my-[1em] [&>a]:underline [&>a]:text-team-secondary whitespace-pre-wrap text-pretty')
        
        if result_span:
            return result_span.text.strip()  # Extract and clean the text
        else:
            print("Could not find the answer on the page.")
            return None
    
    def get_stat(self, query_type: str, query_param: str):
        """Fetch and parse the stat from StatMuse."""
        prompt = prompt_library[query_type](query_param)
        
        html_content = self.fetch_data(prompt.replace(' ', '-'))
        if html_content:
            return self.parse_data(html_content)
        return None
