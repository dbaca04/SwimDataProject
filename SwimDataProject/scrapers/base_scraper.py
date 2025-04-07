"""
Base Scraper Module

This module defines the base scraper class that all source-specific scrapers should inherit from.
"""
import logging
import random
import time
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """
    Base class for all scrapers.
    
    Provides common functionality like session management, rate limiting,
    and proxy rotation that all scrapers can use.
    """
    
    def __init__(self, source_name, base_url, config=None):
        """
        Initialize a new scraper.
        
        Args:
            source_name (str): Name of the data source
            base_url (str): Base URL for the data source
            config (dict, optional): Configuration options
        """
        self.source_name = source_name
        self.base_url = base_url
        self.config = config or {}
        self.session = self._init_session()
        self.logger = self._init_logger()
    
    def _init_session(self):
        """
        Initialize a session with appropriate headers and proxies if needed.
        
        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        if self.config.get('use_proxy', False):
            session.proxies = self._get_proxy()
        
        return session
    
    def _init_logger(self):
        """
        Initialize a logger for this scraper.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger(f"scraper.{self.source_name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_random_user_agent(self):
        """
        Return a random user agent from the pool.
        
        Returns:
            str: User agent string
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.277'
        ]
        return random.choice(user_agents)
    
    def _get_proxy(self):
        """
        Return a proxy from the pool.
        
        Returns:
            dict: Proxy configuration for requests
        """
        # Implementation depends on proxy provider
        # This is a placeholder
        return None
    
    def rate_limit(self, min_seconds=1, max_seconds=3):
        """
        Sleep for a random amount of time to avoid overloading the server.
        
        Args:
            min_seconds (float): Minimum sleep time in seconds
            max_seconds (float): Maximum sleep time in seconds
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)
    
    @abstractmethod
    def scrape(self):
        """
        Main scraping method to be implemented by subclasses.
        
        Returns:
            list: Scraped data
        """
        raise NotImplementedError("Subclasses must implement scrape()")
    
    @abstractmethod
    def save_data(self, data):
        """
        Save scraped data to database.
        
        Args:
            data (list): Data to save
            
        Returns:
            int: Number of records saved
        """
        raise NotImplementedError("Subclasses must implement save_data()")
