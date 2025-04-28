"""
Unit tests for the main USA Swimming scraper module.
"""

import os
import json
import pytest
from unittest import mock
from datetime import datetime

from SwimDataProject.scrapers.usa_swimming.scraper import USASwimmingScraper


class TestUSASwimmingScraper:
    """Tests for the USASwimmingScraper class"""
    
    @pytest.fixture
    def scraper(self, test_config, mock_session):
        """Create a scraper instance with mocked dependencies."""
        with mock.patch('selenium.webdriver.Chrome'):
            with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.IndividualTimesScraper'):
                with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.EventRankingsScraper'):
                    with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.AgeGroupRecordsScraper'):
                        with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.TopTimesScraper'):
                            scraper = USASwimmingScraper(test_config)
                            yield scraper
    
    def test_init(self, test_config, mock_session):
        """Test scraper initialization."""
        with mock.patch('selenium.webdriver.Chrome'):
            with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.IndividualTimesScraper'):
                with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.EventRankingsScraper'):
                    with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.AgeGroupRecordsScraper'):
                        with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.TopTimesScraper'):
                            # Initialize the scraper
                            scraper = USASwimmingScraper(test_config)
                            
                            # Check basic attributes
                            assert scraper.source_name == "usa_swimming"
                            assert scraper.base_url == "https://data.usaswimming.org"
                            assert scraper.config == test_config
                            assert scraper.data_dir == test_config['data_dir']
                            
                            # Should have initialized all component scrapers
                            assert scraper.individual_times_scraper is not None
                            assert scraper.event_rankings_scraper is not None
                            assert scraper.age_group_records_scraper is not None
                            assert scraper.top_times_scraper is not None
                            
                            # Should have initialized stats
                            assert scraper.stats == {
                                'swimmers_processed': 0,
                                'times_extracted': 0,
                                'rankings_extracted': 0,
                                'errors': 0
                            }
    
    def test_init_selenium_driver(self, mock_session):
        """Test Selenium WebDriver initialization."""
        config = {'headless': True}
        
        # Mock ChromeDriverManager if available
        with mock.patch('SwimDataProject.scrapers.usa_swimming.scraper.WEBDRIVER_MANAGER_AVAILABLE', False):
            with mock.patch('selenium.webdriver.Chrome') as mock_chrome:
                with mock.patch('selenium.webdriver.chrome.options.Options') as mock_options:
                    # Mock the options object
                    options_instance = mock.MagicMock()
                    mock_options.return_value = options_instance
                    
                    # Mock the driver instance
                    driver_instance = mock.MagicMock()
                    mock_chrome.return_value = driver_instance
                    
                    # Create a partial scraper object just to test _init_selenium_driver
                    with mock.patch.object(USASwimmingScraper, '_init_session', return_value=mock.MagicMock()):
                        with mock.patch.object(USASwimmingScraper, '_init_logger', return_value=mock.MagicMock()):
                            scraper = USASwimmingScraper(config)
                            
                            # Check WebDriver configuration
                            options_instance.add_argument.assert_any_call('--headless')
                            options_instance.add_argument.assert_any_call('--no-sandbox')
                            options_instance.add_argument.assert_any_call('--disable-dev-shm-usage')
                            
                            # Check anti-detection measures
                            options_instance.add_experimental_option.assert_any_call('excludeSwitches', ['enable-automation'])
                            options_instance.add_experimental_option.assert_any_call('useAutomationExtension', False)
                            
                            # Should have executed CDP command to disable webdriver
                            driver_instance.execute_cdp_cmd.assert_called_once()
                            
                            # Should have set implicit wait
                            assert driver_instance.implicitly_wait.called
    
    def test_scrape_individual_times(self, scraper, sample_individual_times):
        """Test scraping individual times for swimmers."""
        # Configure scraper to scrape individual times
        scraper.config['swimmer_names'] = ['John Smith', 'Jane Doe']
        
        # Mock the individual_times_scraper to return sample data
        mock_individual_times_scraper = scraper.individual_times_scraper
        mock_individual_times_scraper.scrape.side_effect = [
            sample_individual_times,  # For John Smith
            []  # For Jane Doe (no results)
        ]
        
        # Call scrape method
        results = scraper.scrape()
        
        # Check that individual_times_scraper was called for both swimmers
        assert mock_individual_times_scraper.scrape.call_count == 2
        mock_individual_times_scraper.scrape.assert_any_call({'name': 'John Smith'})
        mock_individual_times_scraper.scrape.assert_any_call({'name': 'Jane Doe'})
        
        # Check results
        assert results['individual_times'] == sample_individual_times
        
        # Check stats
        assert scraper.stats['swimmers_processed'] == 2
        assert scraper.stats['times_extracted'] == len(sample_individual_times)
        assert scraper.stats['errors'] == 0
    
    def test_scrape_event_rankings(self, scraper, sample_rankings):
        """Test scraping event rankings."""
        # Configure scraper to scrape event rankings
        scraper.config['event_configs'] = [
            {
                'event': '50 Freestyle',
                'course': 'SCY',
                'gender': 'Male',
                'age_group': '17-18'
            }
        ]
        
        # Mock the event_rankings_scraper to return sample data
        mock_event_rankings_scraper = scraper.event_rankings_scraper
        mock_event_rankings_scraper.scrape.return_value = sample_rankings
        
        # Call scrape method
        results = scraper.scrape()
        
        # Check that event_rankings_scraper was called
        mock_event_rankings_scraper.scrape.assert_called_once_with(scraper.config['event_configs'][0])
        
        # Check results
        assert results['event_rankings'] == sample_rankings
        
        # Check stats
        assert scraper.stats['rankings_extracted'] == len(sample_rankings)
        assert scraper.stats['errors'] == 0
    
    def test_scrape_age_group_records(self, scraper):
        """Test scraping age group records."""
        # Configure scraper to scrape age group records
        scraper.config['scrape_records'] = True
        
        # Mock sample records
        sample_records = [
            {'event': '50 Free', 'age_group': '11-12', 'gender': 'Female', 'time': '23.10'},
            {'event': '100 Free', 'age_group': '11-12', 'gender': 'Female', 'time': '50.22'}
        ]
        
        # Mock the age_group_records_scraper to return sample data
        mock_age_group_records_scraper = scraper.age_group_records_scraper
        mock_age_group_records_scraper.scrape.return_value = sample_records
        
        # Call scrape method
        results = scraper.scrape()
        
        # Check that age_group_records_scraper was called
        mock_age_group_records_scraper.scrape.assert_called_once()
        
        # Check results
        assert results['age_group_records'] == sample_records
    
    def test_scrape_top_times(self, scraper):
        """Test scraping top times."""
        # Configure scraper to scrape top times
        scraper.config['top_times_configs'] = [
            {
                'event': '50 Freestyle',
                'course': 'SCY',
                'gender': 'Female',
                'age_group': '15-16'
            }
        ]
        
        # Mock sample top times
        sample_top_times = [
            {'rank': 1, 'swimmer_name': 'Sophia Rodriguez', 'time': '23.45'},
            {'rank': 2, 'swimmer_name': 'Emily Chen', 'time': '23.67'}
        ]
        
        # Mock the top_times_scraper to return sample data
        mock_top_times_scraper = scraper.top_times_scraper
        mock_top_times_scraper.scrape.return_value = sample_top_times
        
        # Call scrape method
        results = scraper.scrape()
        
        # Check that top_times_scraper was called
        mock_top_times_scraper.scrape.assert_called_once_with(scraper.config['top_times_configs'][0])
        
        # Check results
        assert results['top_times'] == sample_top_times
    
    def test_error_handling(self, scraper):
        """Test error handling during scraping."""
        # Configure scraper to attempt all scrape types
        scraper.config['swimmer_names'] = ['John Smith']
        scraper.config['event_configs'] = [{'event': '50 Freestyle'}]
        scraper.config['scrape_records'] = True
        scraper.config['top_times_configs'] = [{'event': '50 Freestyle'}]
        
        # Make each component scraper raise an exception
        scraper.individual_times_scraper.scrape.side_effect = Exception("Individual times error")
        scraper.event_rankings_scraper.scrape.side_effect = Exception("Event rankings error")
        scraper.age_group_records_scraper.scrape.side_effect = Exception("Age group records error")
        scraper.top_times_scraper.scrape.side_effect = Exception("Top times error")
        
        # Call scrape method - should handle all errors and continue
        results = scraper.scrape()
        
        # Check that all scrapers were attempted
        scraper.individual_times_scraper.scrape.assert_called_once()
        scraper.event_rankings_scraper.scrape.assert_called_once()
        scraper.age_group_records_scraper.scrape.assert_called_once()
        scraper.top_times_scraper.scrape.assert_called_once()
        
        # Check that error stats were updated
        assert scraper.stats['errors'] == 4
        
        # Results should be empty but complete
        assert results['individual_times'] == []
        assert results['event_rankings'] == []
        assert results['age_group_records'] == []
        assert results['top_times'] == []
    
    def test_save_data(self, scraper, tmp_path, sample_individual_times, sample_rankings):
        """Test saving scraped data to files."""
        # Set data_dir to tmp_path
        scraper.data_dir = str(tmp_path)
        
        # Prepare test data
        data = {
            'individual_times': sample_individual_times,
            'event_rankings': sample_rankings,
            'age_group_records': [{'event': '50 Free', 'time': '23.10'}],
            'top_times': [{'rank': 1, 'swimmer_name': 'Sophia Rodriguez', 'time': '23.45'}],
            'stats': scraper.stats
        }
        
        # Mock datetime to get predictable filenames
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 10, 15, 0, 0)
            
            # Call save_data
            scraper.save_data(data)
            
            # Check files were created
            timestamp = '20231210150000'
            
            # Individual times file
            times_file = tmp_path / f'individual_times_{timestamp}.json'
            assert times_file.exists()
            with open(times_file) as f:
                saved_times = json.load(f)
                assert saved_times == sample_individual_times
            
            # Event rankings file
            rankings_file = tmp_path / f'event_rankings_{timestamp}.json'
            assert rankings_file.exists()
            with open(rankings_file) as f:
                saved_rankings = json.load(f)
                assert saved_rankings == sample_rankings
            
            # Age group records file
            records_file = tmp_path / f'age_group_records_{timestamp}.json'
            assert records_file.exists()
            with open(records_file) as f:
                saved_records = json.load(f)
                assert saved_records == data['age_group_records']
            
            # Top times file
            top_times_file = tmp_path / f'top_times_{timestamp}.json'
            assert top_times_file.exists()
            with open(top_times_file) as f:
                saved_top_times = json.load(f)
                assert saved_top_times == data['top_times']
            
            # Stats file
            stats_file = tmp_path / f'stats_{timestamp}.json'
            assert stats_file.exists()
            with open(stats_file) as f:
                saved_stats = json.load(f)
                assert saved_stats == data['stats']
    
    def test_save_data_no_data(self, scraper, caplog):
        """Test save_data behavior with no data."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Call save_data with no data
        scraper.save_data(None)
        
        # Should log a warning and return without error
        assert "No data to save" in caplog.text
    
    def test_cleanup(self, scraper):
        """Test cleanup on deletion."""
        # Mock the driver
        mock_driver = mock.MagicMock()
        scraper.driver = mock_driver
        
        # Call __del__
        scraper.__del__()
        
        # Should have called quit on the driver
        mock_driver.quit.assert_called_once()
