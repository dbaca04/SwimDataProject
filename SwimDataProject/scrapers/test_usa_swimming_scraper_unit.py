"""
Unit tests for USA Swimming scraper.

These tests verify that the USA Swimming scraper functionality works correctly.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from scrapers.usa_swimming_scraper import USASwimmingScraper


class TestUSASwimmingScraper:
    """Tests for the USA Swimming scraper class."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked Selenium driver."""
        with patch('scrapers.usa_swimming_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.usa_swimming_scraper.ChromeDriverManager'):
                # Create scraper with headless mode enabled
                scraper = USASwimmingScraper({'headless': True})
                # Return both scraper and the mock driver for testing
                yield scraper, mock_driver
    
    def test_init(self, scraper):
        """Test initialization of the scraper."""
        scraper_instance, mock_driver = scraper
        
        assert scraper_instance.source_name == "usa_swimming"
        assert scraper_instance.base_url == "https://data.usaswimming.org"
        assert isinstance(scraper_instance.config, dict)
        assert scraper_instance.config.get('headless') is True
        assert scraper_instance.driver is not None
        
        # Verify Selenium configuration
        mock_driver.assert_called_once()
    
    def test_init_selenium_driver(self):
        """Test Selenium driver initialization with different configurations."""
        with patch('scrapers.usa_swimming_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.usa_swimming_scraper.ChromeDriverManager'):
                with patch('scrapers.usa_swimming_scraper.Options') as mock_options:
                    options_instance = MagicMock()
                    mock_options.return_value = options_instance
                    
                    # Test with headless mode
                    USASwimmingScraper({'headless': True})
                    options_instance.add_argument.assert_any_call('--headless')
                    
                    # Reset mocks
                    mock_options.reset_mock()
                    options_instance = MagicMock()
                    mock_options.return_value = options_instance
                    
                    # Test without headless mode
                    USASwimmingScraper({'headless': False})
                    # Should not have added headless argument
                    headless_calls = [call for call in options_instance.add_argument.call_args_list 
                                      if call[0][0] == '--headless']
                    assert len(headless_calls) == 0
    
    def test_cleanup(self):
        """Test cleanup functionality in __del__ method."""
        with patch('scrapers.usa_swimming_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.usa_swimming_scraper.ChromeDriverManager'):
                driver_instance = MagicMock()
                mock_driver.return_value = driver_instance
                
                # Create scraper
                scraper = USASwimmingScraper()
                
                # Explicitly call __del__ (normally called by garbage collection)
                scraper.__del__()
                
                # Verify driver quit was called
                driver_instance.quit.assert_called_once()
    
    def test_convert_time_to_seconds(self, scraper):
        """Test time conversion functionality."""
        scraper_instance, _ = scraper
        
        # Test MM:SS.ss format
        assert scraper_instance._convert_time_to_seconds("1:23.45") == 83.45
        
        # Test SS.ss format
        assert scraper_instance._convert_time_to_seconds("45.67") == 45.67
        
        # Test edge cases
        assert scraper_instance._convert_time_to_seconds("0:00.01") == 0.01
        assert scraper_instance._convert_time_to_seconds("10:00.00") == 600.0
        
        # Test with invalid input
        with patch.object(scraper_instance, 'logger') as mock_logger:
            result = scraper_instance._convert_time_to_seconds("invalid")
            assert result is None
            mock_logger.warning.assert_called_once()
    
    @patch('scrapers.usa_swimming_scraper.WebDriverWait')
    def test_fill_search_form(self, mock_wait, scraper):
        """Test form filling functionality."""
        scraper_instance, _ = scraper
        
        # Mock driver elements and interactions
        scraper_instance.driver = MagicMock()
        
        # Create mock elements for form fields
        mock_elements = {
            'first_name': MagicMock(),
            'last_name': MagicMock(),
            'gender': MagicMock(),
            'min_age': MagicMock(),
            'max_age': MagicMock(),
            'team': MagicMock(),
            'state': MagicMock(),
            'start_date': MagicMock(),
            'end_date': MagicMock(),
            'event': MagicMock(),
            'course': MagicMock(),
            'search_button': MagicMock()
        }
        
        # Setup driver.find_element to return appropriate mocks
        def find_element_side_effect(by, value):
            if value == "search-first-name":
                return mock_elements['first_name']
            elif value == "search-last-name":
                return mock_elements['last_name']
            elif value == "search-gender":
                return mock_elements['gender']
            elif value == "search-min-age":
                return mock_elements['min_age']
            elif value == "search-max-age":
                return mock_elements['max_age']
            elif value == "search-team":
                return mock_elements['team']
            elif value == "search-state":
                return mock_elements['state']
            elif value == "search-start-date":
                return mock_elements['start_date']
            elif value == "search-end-date":
                return mock_elements['end_date']
            elif value == "search-event":
                return mock_elements['event']
            elif value == "search-course":
                return mock_elements['course']
            elif value == "search-submit":
                return mock_elements['search_button']
        
        scraper_instance.driver.find_element.side_effect = find_element_side_effect
        
        # Setup mock gender, state, event options
        mock_elements['gender'].find_element.return_value = MagicMock()
        mock_elements['state'].find_element.return_value = MagicMock()
        mock_elements['event'].find_element.return_value = MagicMock()
        mock_elements['course'].find_element.return_value = MagicMock()
        
        # Create search parameters for testing
        search_params = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'M',
            'min_age': 15,
            'max_age': 18,
            'team': 'Test Team',
            'state': 'California',
            'start_date': '01/01/2024',
            'end_date': '12/31/2024',
            'event': '100 Freestyle',
            'course': 'SCY'
        }
        
        # Call the method
        with patch.object(scraper_instance, 'rate_limit'):
            scraper_instance._fill_search_form(search_params)
        
        # Verify form interactions
        mock_elements['first_name'].clear.assert_called_once()
        mock_elements['first_name'].send_keys.assert_called_once_with('John')
        
        mock_elements['last_name'].clear.assert_called_once()
        mock_elements['last_name'].send_keys.assert_called_once_with('Doe')
        
        mock_elements['gender'].find_element.assert_called_once()
        
        mock_elements['min_age'].clear.assert_called_once()
        mock_elements['min_age'].send_keys.assert_called_once_with('15')
        
        mock_elements['max_age'].clear.assert_called_once()
        mock_elements['max_age'].send_keys.assert_called_once_with('18')
        
        mock_elements['team'].clear.assert_called_once()
        mock_elements['team'].send_keys.assert_called_once_with('Test Team')
        
        mock_elements['state'].find_element.assert_called_once()
        
        mock_elements['start_date'].clear.assert_called_once()
        mock_elements['start_date'].send_keys.assert_called_once_with('01/01/2024')
        
        mock_elements['end_date'].clear.assert_called_once()
        mock_elements['end_date'].send_keys.assert_called_once_with('12/31/2024')
        
        mock_elements['event'].find_element.assert_called_once()
        
        mock_elements['course'].find_element.assert_called_once()
        
        mock_elements['search_button'].click.assert_called_once()
