# Standard library imports
import logging
import time
import random

# Third-party imports
import requests
from bs4 import BeautifulSoup

# Local application imports
from proxy import Proxy

AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

class Scraper:
    # static variable
    scraped = 1
    
    def __init__(self, use_proxy: bool, logger: logging.Logger = None):
        self.proxy = Proxy(logger) if use_proxy else None
        self.logger = logger
            
    # PUBLIC METHODS

    def scrape(self, url: str, scrape_depth: int = 0) -> BeautifulSoup:
        """ Scrapes a URL and returns a BeautifulSoup object """
        if scrape_depth > 3:
            self.logger.error(f"Failed to scrape {url} after 3 attempts")
            return None
        
        try:
            proxy = self.proxy.get_proxy() if self.proxy else None
            
            # Pause for a few seconds to avoid IP ban on local
            if not proxy:
                self.logger.info(f"Pausing for {Scraper.scraped} seconds to avoid IP ban")
                time.sleep(Scraper.scraped)
                
                Scraper.scraped = Scraper.scraped + 1 if Scraper.scraped < 5 else 1
            
            response = requests.get(url, proxies=proxy, headers = {'User-Agent': random.choice(AGENTS)})
            if response.status_code == 200:
                self.logger.info(f"Successfully scraped {url}")
                soup = self.__make_soup(response.text)
                
                if soup: 
                    return soup
                else:
                    self.logger.warning(f"Failed to create soup for {url}, retrying")
                    return self.scrape(url, scrape_depth + 1)
            
            else:
                self.logger.warning(f"Failed to scrape {url}")
                print(response.content)
                return self.scrape(url, scrape_depth + 1)
                
        except Exception as e:
            self.logger.error(f"Error connecting to {url}: {e}")
            return self.scrape(url, scrape_depth + 1)
    
    # PRIVATE METHODS
    
    def __make_soup(self, response_text: str) -> BeautifulSoup:
        """Fetches the URL and parses its content with BeautifulSoup """
        try:
            return BeautifulSoup(response_text, 'html.parser')
        except Exception as e:
            return None