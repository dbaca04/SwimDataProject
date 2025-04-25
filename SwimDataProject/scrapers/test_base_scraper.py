"""
Unit tests for BaseScraper class.

These tests verify that the common scraping functionality works correctly.
"""
import pytest
import requests
from unittest.mock import patch, MagicMock, call
import random
import time
import logging
from scrapers.base_scraper import BaseScraper


class TestScraperImpl(BaseScraper):
    """Implementation of BaseScraper for testing."""
    
    def scrape(self):
        """Implement abstract method for testing."""
        return ["test_data"]
    
    def save_data(self, data):
        """Implement abstract method for testing."""
        return len(data)


class TestBaseScraper:
    """Tests for the BaseScraper class."""
    
    @pytest.fixture
    def scraper(self):
        """Create a test scraper instance."""
        return TestScraperImpl("test_source", "https://example.com")
    
    def test_init(self, scraper):
        """Test initialization of the scraper."""
        assert scraper.source_name == "test_source"
        assert scraper.base_url == "https://example.com"
        assert isinstance(scraper.config, dict)
        assert isinstance(scraper.session, requests.Session)
        assert isinstance(scraper.logger, logging.Logger)
    
    def test_init_with_config(self):
        """Test initialization with custom config."""
        config = {"key": "value", "use_proxy": True}
        with patch.object(TestScraperImpl, '_get_proxy', return_value={"http": "http://proxy.example.com"}):
            scraper = TestScraperImpl("test_source", "https://example.com", config)
            assert scraper.config == config
            assert scraper.session.proxies == {"http": "http://proxy.example.com"}
    
    def test_get_random_user_agent(self, scraper):
        """Test user agent rotation."""
        user_agent = scraper._get_random_user_agent()
        assert isinstance(user_agent, str)
        assert len(user_agent) > 10  # Basic validation that it's not empty
        
        # Test multiple calls return different agents
        user_agents = set(scraper._get_random_user_agent() for _ in range(10))
        assert len(user_agents) > 1, "User agent rotation not working"
    
    @patch('time.sleep')
    def test_rate_limit(self, mock_sleep, scraper):
        """Test rate limiting functionality."""
        # Test with default arguments
        scraper.rate_limit()
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert 1 <= sleep_time <= 3
        
        mock_sleep.reset_mock()
        
        # Test with custom arguments
        scraper.rate_limit(5, 10)
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert 5 <= sleep_time <= 10
    
    def test_get_proxy(self, scraper):
        """Test proxy getter method."""
        proxy = scraper._get_proxy()
        assert proxy is None  # Default implementation returns None
    
    @patch.object(TestScraperImpl, 'scrape')
    def test_abstract_method_implementation(self, mock_scrape, scraper):
        """Test that abstract methods are implemented."""
        mock_scrape.return_value = ["data1", "data2"]
        
        data = scraper.scrape()
        assert data == ["data1", "data2"]
        
        records_saved = scraper.save_data(data)
        assert records_saved == 2
    
    @patch('requests.Session.get')
    def test_session_headers(self, mock_get, scraper):
        """Test that session has proper headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>test</html>"
        mock_get.return_value = mock_response
        
        scraper.session.get("https://example.com")
        
        # Verify headers in the request
        headers = mock_get.call_args[1].get('headers', {})
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Referer" in headers
        assert headers.get("Referer") == "https://example.com"
    
    def test_logger_configuration(self, scraper):
        """Test logger configuration."""
        logger = scraper.logger
        assert logger.name == "scraper.test_source"
        assert logger.level <= logging.INFO
