# Standard library imports
import io
import logging
import os

# Third-party imports
import requests

class Proxy:
    def __init__(self, logger: logging.Logger = None):
        self.proxies = []
        self.pointer = 0
        
        self.logger = logger  
    
        proxy_file = os.path.join(os.path.dirname(__file__), 'proxies.txt')
        with io.open(proxy_file, 'r') as f:
            self.proxies = f.read().splitlines()
     
    # PUBLIC METHODS
    
    def get_proxy(self) -> str:
        """ Get the current proxy """
        proxy_checks = 0
        
        while proxy_checks < len(self.proxies):
            proxy = self.proxies[self.pointer]
            formatted_proxy = self.__format_proxy(proxy)
            
            if self.__test_proxy(formatted_proxy):
                self.logger.info(f"Using proxy: {formatted_proxy}")
                return formatted_proxy
            
            self.__rotate_proxy()
            
            proxy_checks += 1
            
        self.logger.error("No working proxies found, continuing without proxy")
        return None
    
    # PRIVATE METHODS 
    
    def __rotate_proxy(self) -> None:
        """ Rotate the proxy """
        self.pointer = (self.pointer + 1) % len(self.proxies)
        
    def __test_proxy(self, proxy: dict) -> None:
        """ Test if a proxy is working """
        try:
            requests.get('http://httpbin.org/ip', proxies=proxy, timeout=5)
            return True
        except:
            return False
        
    def __format_proxy(self, proxy) -> dict:
        """ Format a proxy """
        protocol = 'https' if 'https' in proxy else 'http'
        return { protocol: proxy }