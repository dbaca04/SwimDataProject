"""
Unit tests for the base scraper classes.
"""

import time
import pytest
from unittest import mock

from SwimDataProject.scrapers.base_scraper import SwimScraper, RateLimiter, ProxyManager


class TestRateLimiter:
    """Tests for the RateLimiter class"""
    
    def test_init(self):
        """Test initialization with default and custom values."""
        # Default values
        limiter = RateLimiter()
        assert limiter.requests_per_minute == 10
        assert limiter.requests_per_hour == 100
        assert limiter.minute_requests == []
        assert limiter.hour_requests == []
        
        # Custom values
        limiter = RateLimiter(requests_per_minute=20, requests_per_hour=200)
        assert limiter.requests_per_minute == 20
        assert limiter.requests_per_hour == 200
    
    def test_wait_if_needed_no_wait(self):
        """Test wait_if_needed when no waiting is required."""
        limiter = RateLimiter(requests_per_minute=5, requests_per_hour=10)
        
        # No requests yet, should not wait
        start_time = time.time()
        limiter.wait_if_needed()
        end_time = time.time()
        
        # Should be very quick, under 0.1 seconds
        assert end_time - start_time < 0.1
        assert len(limiter.minute_requests) == 1
        assert len(limiter.hour_requests) == 1
    
    def test_wait_if_needed_minute_limit(self):
        """Test wait_if_needed when minute limit is reached."""
        limiter = RateLimiter(requests_per_minute=2, requests_per_hour=100)
        
        # Add requests just under a minute ago
        now = time.time()
        limiter.minute_requests = [now - 59, now - 58]
        
        with mock.patch('time.sleep') as mock_sleep:
            limiter.wait_if_needed()
            # Should have tried to sleep
            mock_sleep.assert_called_once()
            # Sleep duration should be around 57-59 seconds plus random addition
            args = mock_sleep.call_args[0]
            assert 57 <= args[0] <= 60
    
    def test_wait_if_needed_hour_limit(self):
        """Test wait_if_needed when hour limit is reached."""
        limiter = RateLimiter(requests_per_minute=100, requests_per_hour=2)
        
        # Add requests just under an hour ago
        now = time.time()
        limiter.hour_requests = [now - 3590, now - 3580]
        
        with mock.patch('time.sleep') as mock_sleep:
            limiter.wait_if_needed()
            # Should have tried to sleep
            mock_sleep.assert_called_once()
            # Sleep duration should be around 3570-3590 seconds plus random addition
            args = mock_sleep.call_args[0]
            assert 3570 <= args[0] <= 3595
    
    def test_cleanup_old_timestamps(self):
        """Test that old timestamps are cleaned up."""
        limiter = RateLimiter()
        
        # Add some old timestamps
        now = time.time()
        limiter.minute_requests = [now - 70, now - 30]  # One old, one new
        limiter.hour_requests = [now - 3700, now - 1800]  # One old, one new
        
        limiter.wait_if_needed()
        
        # Old timestamps should be removed
        assert len(limiter.minute_requests) == 2  # Original new one + new request
        assert now - 35 <= limiter.minute_requests[0] <= now - 25  # The remaining original
        
        assert len(limiter.hour_requests) == 2  # Original new one + new request
        assert now - 1850 <= limiter.hour_requests[0] <= now - 1750  # The remaining original


class TestProxyManager:
    """Tests for the ProxyManager class"""
    
    def test_init_empty(self):
        """Test initialization with no proxy sources."""
        manager = ProxyManager()
        assert manager.proxies == []
        assert manager.proxy_performance == {}
    
    @mock.patch('requests.get')
    def test_load_proxies_from_url(self, mock_get):
        """Test loading proxies from URL."""
        # Mock the response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1.1.1.1:8080\n2.2.2.2:8080\n3.3.3.3:8080"
        mock_get.return_value = mock_response
        
        manager = ProxyManager()
        manager.load_proxies_from_url("http://example.com/proxies")
        
        # Should have loaded 3 proxies
        assert len(manager.proxies) == 3
        assert "1.1.1.1:8080" in manager.proxies
        assert "2.2.2.2:8080" in manager.proxies
        assert "3.3.3.3:8080" in manager.proxies
    
    def test_load_proxies_from_file(self, tmp_path):
        """Test loading proxies from file."""
        # Create a temporary proxies file
        proxy_file = tmp_path / "proxies.txt"
        proxy_file.write_text("1.1.1.1:8080\n2.2.2.2:8080\n3.3.3.3:8080")
        
        manager = ProxyManager()
        manager.load_proxies_from_file(str(proxy_file))
        
        # Should have loaded 3 proxies
        assert len(manager.proxies) == 3
        assert "1.1.1.1:8080" in manager.proxies
        assert "2.2.2.2:8080" in manager.proxies
        assert "3.3.3.3:8080" in manager.proxies
    
    def test_get_proxy_empty(self):
        """Test get_proxy with no proxies."""
        manager = ProxyManager()
        assert manager.get_proxy() is None
    
    def test_get_proxy_with_proxies(self):
        """Test get_proxy with available proxies."""
        manager = ProxyManager()
        manager.proxies = ["1.1.1.1:8080", "2.2.2.2:8080", "3.3.3.3:8080"]
        
        # Get a proxy
        proxy = manager.get_proxy()
        assert proxy in manager.proxies
    
    def test_get_proxy_with_performance_data(self):
        """Test get_proxy with performance data."""
        manager = ProxyManager()
        manager.proxies = ["1.1.1.1:8080", "2.2.2.2:8080", "3.3.3.3:8080"]
        
        # Set performance data to prefer the second proxy
        manager.proxy_performance = {
            "1.1.1.1:8080": -1,  # Bad performance
            "2.2.2.2:8080": 5,   # Good performance
            "3.3.3.3:8080": 3    # OK performance
        }
        
        # Test many get_proxy calls - should never return the bad proxy
        results = [manager.get_proxy() for _ in range(50)]
        assert "1.1.1.1:8080" not in results
        assert "2.2.2.2:8080" in results
        assert "3.3.3.3:8080" in results
    
    def test_report_proxy_success(self):
        """Test reporting proxy success."""
        manager = ProxyManager()
        
        # New proxy starts at score 0, should go to 1
        manager.report_proxy_success("1.1.1.1:8080")
        assert manager.proxy_performance["1.1.1.1:8080"] == 1
        
        # Report multiple successes, should cap at 10
        for _ in range(15):
            manager.report_proxy_success("1.1.1.1:8080")
        assert manager.proxy_performance["1.1.1.1:8080"] == 10
    
    def test_report_proxy_failure(self):
        """Test reporting proxy failure."""
        manager = ProxyManager()
        
        # Set initial score
        manager.proxy_performance["1.1.1.1:8080"] = 5
        
        # Report failure, should subtract 2
        manager.report_proxy_failure("1.1.1.1:8080")
        assert manager.proxy_performance["1.1.1.1:8080"] == 3
        
        # Report more failures, should reach minimum of -5
        for _ in range(10):
            manager.report_proxy_failure("1.1.1.1:8080")
        assert manager.proxy_performance["1.1.1.1:8080"] == -5
    
    def test_remove_failing_proxy(self):
        """Test that consistently failing proxies are removed."""
        manager = ProxyManager()
        manager.proxies = ["1.1.1.1:8080", "2.2.2.2:8080"]
        
        # Set score to -4 (one failure away from removal)
        manager.proxy_performance["1.1.1.1:8080"] = -4
        
        # Report one more failure, should remove it
        manager.report_proxy_failure("1.1.1.1:8080")
        assert "1.1.1.1:8080" not in manager.proxies
        assert len(manager.proxies) == 1
        assert manager.proxies[0] == "2.2.2.2:8080"


class TestSwimScraper:
    """Tests for the SwimScraper base class"""
    
    # Create a concrete subclass for testing the abstract base class
    class ConcreteSwimScraper(SwimScraper):
        def scrape(self):
            return {"test": "data"}
    
    def test_init(self, mock_session):
        """Test initialization with config."""
        config = {
            'requests_per_minute': 15,
            'requests_per_hour': 150,
            'use_proxy': False
        }
        
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Check basic attributes
        assert scraper.source_name == "test_source"
        assert scraper.base_url == "https://example.com"
        assert scraper.config == config
        
        # Check rate limiter configuration
        assert scraper.rate_limiter.requests_per_minute == 15
        assert scraper.rate_limiter.requests_per_hour == 150
        
        # Check proxy manager
        assert scraper.proxy_manager is None  # because use_proxy is False
    
    def test_init_with_proxy(self, mock_session):
        """Test initialization with proxy support."""
        config = {
            'use_proxy': True,
            'proxy_list_url': 'http://example.com/proxies'
        }
        
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Should have created a proxy manager
        assert scraper.proxy_manager is not None
    
    def test_get_random_user_agent(self):
        """Test that random user agent is returned from the pool."""
        config = {}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Get 100 user agents, should get different ones
        user_agents = [scraper._get_random_user_agent() for _ in range(100)]
        
        # Should have at least 2 unique user agents
        assert len(set(user_agents)) >= 2
    
    def test_rate_limited_request(self, mock_session):
        """Test rate-limited request method."""
        config = {}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Mock the rate_limiter
        with mock.patch.object(scraper.rate_limiter, 'wait_if_needed') as mock_wait:
            response = scraper._rate_limited_request("https://example.com/test")
            
            # Should have called rate limiter
            mock_wait.assert_called_once()
            
            # Should have made the request
            scraper.session.request.assert_called_once_with('GET', 'https://example.com/test')
            
            # Should return the response
            assert response == scraper.session.request.return_value
    
    def test_rate_limited_request_retry(self, mock_session):
        """Test retry behavior for failed requests."""
        config = {'max_retries': 3}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Make the first two requests fail, third succeed
        side_effects = [
            Exception("First failure"),
            Exception("Second failure"),
            mock.MagicMock(status_code=200)
        ]
        scraper.session.request.side_effect = side_effects
        
        # Mock sleep to avoid actually waiting
        with mock.patch('time.sleep'):
            response = scraper._rate_limited_request("https://example.com/test")
            
            # Should have made 3 requests (2 failures + 1 success)
            assert scraper.session.request.call_count == 3
            
            # Should return the successful response
            assert response.status_code == 200
    
    def test_rate_limited_request_all_retries_fail(self, mock_session):
        """Test behavior when all retries fail."""
        config = {'max_retries': 2}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Make all requests fail
        scraper.session.request.side_effect = Exception("Request failed")
        
        # Mock sleep to avoid actually waiting
        with mock.patch('time.sleep'):
            # Should raise exception when all retries fail
            with pytest.raises(Exception, match="All 2 request attempts failed"):
                scraper._rate_limited_request("https://example.com/test")
            
            # Should have tried the configured number of times
            assert scraper.session.request.call_count == 2
    
    def test_save_data(self, caplog):
        """Test the default save_data implementation logs but doesn't save."""
        import logging
        caplog.set_level(logging.INFO)
        
        config = {}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Try to save a list of data
        test_data = [{"id": 1}, {"id": 2}]
        scraper.save_data(test_data)
        
        # Should have logged a message about saving, but not actually saved
        assert "Would save 2 records" in caplog.text
    
    def test_concrete_scrape(self):
        """Test that a concrete implementation of scrape works."""
        config = {}
        scraper = self.ConcreteSwimScraper("test_source", "https://example.com", config)
        
        # Call the concrete implementation
        result = scraper.scrape()
        
        # Should return the test data from our concrete implementation
        assert result == {"test": "data"}
