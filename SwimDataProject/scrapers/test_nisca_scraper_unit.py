"""
Unit tests for NISCA scraper.

These tests verify that the NISCA scraper functionality works correctly.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from scrapers.nisca_scraper import NIScAScraper


class TestNIScAScraper:
    """Tests for the NISCA scraper class."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked Selenium driver."""
        with patch('scrapers.nisca_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.nisca_scraper.ChromeDriverManager'):
                # Create scraper with headless mode enabled
                scraper = NIScAScraper({'headless': True})
                # Return both scraper and the mock driver for testing
                yield scraper, mock_driver
    
    def test_init(self, scraper):
        """Test initialization of the scraper."""
        scraper_instance, mock_driver = scraper
        
        assert scraper_instance.source_name == "nisca"
        assert scraper_instance.base_url == "https://niscaonline.org"
        assert isinstance(scraper_instance.config, dict)
        assert scraper_instance.config.get('headless') is True
        assert scraper_instance.driver is not None
        
        # Verify Selenium configuration
        mock_driver.assert_called_once()
    
    def test_init_selenium_driver(self):
        """Test Selenium driver initialization with different configurations."""
        with patch('scrapers.nisca_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.nisca_scraper.ChromeDriverManager'):
                with patch('scrapers.nisca_scraper.Options') as mock_options:
                    options_instance = MagicMock()
                    mock_options.return_value = options_instance
                    
                    # Test with headless mode
                    NIScAScraper({'headless': True})
                    options_instance.add_argument.assert_any_call('--headless')
                    
                    # Reset mocks
                    mock_options.reset_mock()
                    options_instance = MagicMock()
                    mock_options.return_value = options_instance
                    
                    # Test without headless mode
                    NIScAScraper({'headless': False})
                    # Should not have added headless argument
                    headless_calls = [call for call in options_instance.add_argument.call_args_list 
                                      if call[0][0] == '--headless']
                    assert len(headless_calls) == 0
    
    def test_cleanup(self):
        """Test cleanup functionality in __del__ method."""
        with patch('scrapers.nisca_scraper.webdriver.Chrome') as mock_driver:
            with patch('scrapers.nisca_scraper.ChromeDriverManager'):
                driver_instance = MagicMock()
                mock_driver.return_value = driver_instance
                
                # Create scraper
                scraper = NIScAScraper()
                
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
            
        # Test with None input
        with patch.object(scraper_instance, 'logger') as mock_logger:
            result = scraper_instance._convert_time_to_seconds(None)
            assert result is None
            mock_logger.warning.assert_called_once()
    
    def test_clean_event_name(self, scraper):
        """Test event name cleaning functionality."""
        scraper_instance, _ = scraper
        
        # Test basic cleaning
        assert scraper_instance._clean_event_name("Boys National Record 50 Freestyle") == "50 Freestyle"
        assert scraper_instance._clean_event_name("Girls 100 Free") == "100 Freestyle"
        assert scraper_instance._clean_event_name("Boys 200 IM") == "200 Individual Medley"
        
        # Test with unnecessary spaces and text
        assert scraper_instance._clean_event_name("  Boys  100 Backstroke  National Record  ") == "100 Backstroke"
        
        # Test with unknown event
        assert scraper_instance._clean_event_name("Unknown Event") == "Unknown Event"
    
    def test_parse_event_name(self, scraper):
        """Test event name parsing functionality."""
        scraper_instance, _ = scraper
        
        # Test freestyle event
        result = scraper_instance._parse_event_name("50 Freestyle")
        assert result['distance'] == 50
        assert result['stroke'] == "Freestyle"
        assert result['is_relay'] == False
        
        # Test individual medley
        result = scraper_instance._parse_event_name("200 Individual Medley")
        assert result['distance'] == 200
        assert result['stroke'] == "Individual Medley"
        assert result['is_relay'] == False
        
        # Test relay event
        result = scraper_instance._parse_event_name("200 Medley Relay")
        assert result['distance'] == 200
        assert result['stroke'] == "Medley Relay"
        assert result['is_relay'] == True
        
        # Test with unknown event
        result = scraper_instance._parse_event_name("Unknown Event")
        assert result['distance'] == 0
        assert result['stroke'] == "Unknown"
        assert result['is_relay'] == False
    
    def test_extract_records(self, scraper):
        """Test record extraction from HTML."""
        scraper_instance, _ = scraper
        
        # Create sample HTML for testing
        html = """
        <table>
            <caption>50 Freestyle National Record</caption>
            <tr>
                <th>Record Type</th>
                <th>Time</th>
                <th>Name</th>
                <th>School</th>
                <th>Year</th>
            </tr>
            <tr>
                <td>National Record</td>
                <td>19.43</td>
                <td>John Doe</td>
                <td>High School A</td>
                <td>2024</td>
            </tr>
            <tr>
                <td>Public School</td>
                <td>19.65</td>
                <td>Jane Smith</td>
                <td>High School B</td>
                <td>2023</td>
            </tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        records = scraper_instance._extract_records(soup, "male")
        
        # Check records are extracted correctly
        assert len(records) == 2
        
        # Check first record
        record_key = "50 Freestyle-National Record"
        assert record_key in records
        assert records[record_key]['event'] == "50 Freestyle"
        assert records[record_key]['time'] == "19.43"
        assert records[record_key]['name'] == "John Doe"
        assert records[record_key]['school'] == "High School A"
        assert records[record_key]['year'] == "2024"
        assert records[record_key]['gender'] == "male"
        
        # Check second record
        record_key = "50 Freestyle-Public School"
        assert record_key in records
        assert records[record_key]['event'] == "50 Freestyle"
        assert records[record_key]['time'] == "19.65"
        assert records[record_key]['name'] == "Jane Smith"
        assert records[record_key]['school'] == "High School B"
        assert records[record_key]['year'] == "2023"
        assert records[record_key]['gender'] == "male"
    
    def test_extract_all_america_links(self, scraper):
        """Test extraction of All-America links from HTML."""
        scraper_instance, _ = scraper
        
        # Create sample HTML for testing
        html = """
        <article>
            <h2>All-America Lists</h2>
            <ul>
                <li><a href="/index.php/all-america/2023-2024-boys">2023-2024 Boys All-America</a></li>
                <li><a href="/index.php/all-america/2023-2024-girls">2023-2024 Girls All-America</a></li>
                <li><a href="/index.php/all-america/2022-2023-boys">2022-2023 Boys All-America</a></li>
                <li><a href="/index.php/all-america/2022-2023-girls">2022-2023 Girls All-America</a></li>
            </ul>
        </article>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        links = scraper_instance._extract_all_america_links(soup)
        
        # Check links are extracted correctly
        assert len(links) == 2  # Two years
        
        # Check first year
        assert "2023-2024" in links
        assert "Boys" in links["2023-2024"]
        assert "Girls" in links["2023-2024"]
        assert links["2023-2024"]["Boys"] == "https://niscaonline.org/index.php/all-america/2023-2024-boys"
        assert links["2023-2024"]["Girls"] == "https://niscaonline.org/index.php/all-america/2023-2024-girls"
        
        # Check second year
        assert "2022-2023" in links
        assert "Boys" in links["2022-2023"]
        assert "Girls" in links["2022-2023"]
        assert links["2022-2023"]["Boys"] == "https://niscaonline.org/index.php/all-america/2022-2023-boys"
        assert links["2022-2023"]["Girls"] == "https://niscaonline.org/index.php/all-america/2022-2023-girls"
