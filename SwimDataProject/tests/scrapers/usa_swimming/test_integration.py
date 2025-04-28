"""
Integration tests for the USA Swimming scrapers.
These tests verify that different scrapers work together correctly.
"""

import os
import json
import pytest
from unittest import mock
from datetime import datetime

from SwimDataProject.scrapers.usa_swimming.scraper import USASwimmingScraper
from SwimDataProject.scrapers.usa_swimming_scraper import scrape_usa_swimming


@pytest.mark.integration
@pytest.mark.slow
class TestUSASwimmingIntegration:
    """Integration tests for USA Swimming scrapers"""
    
    @pytest.fixture
    def mock_all_scrapers(self):
        """Mock all component scrapers for integration testing."""
        with mock.patch('SwimDataProject.scrapers.usa_swimming.individual_times.IndividualTimesScraper') as mock_individual:
            with mock.patch('SwimDataProject.scrapers.usa_swimming.event_rankings.EventRankingsScraper') as mock_rankings:
                with mock.patch('SwimDataProject.scrapers.usa_swimming.age_group_records.AgeGroupRecordsScraper') as mock_records:
                    with mock.patch('SwimDataProject.scrapers.usa_swimming.top_times.TopTimesScraper') as mock_top_times:
                        # Setup return values
                        mock_individual.return_value.scrape.return_value = [
                            {
                                'swimmer_name': 'John Smith',
                                'age': 16,
                                'team': 'FAST',
                                'event': '100 Free SCY',
                                'time': '49.32',
                                'time_seconds': 49.32,
                                'meet_name': '2023 Regional Championships',
                                'meet_date': '12/03/2023'
                            }
                        ]
                        
                        mock_rankings.return_value.scrape.return_value = [
                            {
                                'rank': 1,
                                'swimmer_name': 'Alex Johnson',
                                'age': 17,
                                'team': 'SWIM',
                                'time': '20.14',
                                'time_seconds': 20.14,
                                'event': '50 Freestyle',
                                'gender': 'Male'
                            }
                        ]
                        
                        mock_records.return_value.scrape.return_value = [
                            {
                                'event': '50 Free',
                                'time': '23.10',
                                'swimmer_name': 'Sarah Martinez',
                                'team': 'GSC',
                                'date': '12/10/2022',
                                'age_group': '11-12',
                                'gender': 'Female'
                            }
                        ]
                        
                        mock_top_times.return_value.scrape.return_value = [
                            {
                                'rank': 1,
                                'swimmer_name': 'Sophia Rodriguez',
                                'age': 15,
                                'team': 'WAVE',
                                'time': '23.45',
                                'event': '50 Freestyle',
                                'gender': 'Female'
                            }
                        ]
                        
                        yield {
                            'individual': mock_individual,
                            'rankings': mock_rankings,
                            'records': mock_records,
                            'top_times': mock_top_times
                        }
    
    @pytest.mark.parametrize("save_to_file", [True, False])
    def test_full_scrape_process(self, mock_all_scrapers, tmp_path, save_to_file):
        """Test the complete scraping process with all scraper types."""
        # Setup configuration
        config = {
            'save_to_file': save_to_file,
            'data_dir': str(tmp_path),
            'swimmer_names': ['John Smith', 'Jane Doe'],
            'event_configs': [
                {
                    'event': '50 Freestyle',
                    'course': 'SCY',
                    'age_group': '17-18',
                    'gender': 'Male'
                }
            ],
            'scrape_records': True,
            'top_times_configs': [
                {
                    'event': '50 Freestyle',
                    'course': 'SCY',
                    'age_group': '15-16',
                    'gender': 'Female'
                }
            ]
        }
        
        # Mock Selenium WebDriver
        with mock.patch('selenium.webdriver.Chrome'):
            # Mock datetime for predictable filenames
            with mock.patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 12, 10, 15, 0, 0)
                
                # Call the main scrape_usa_swimming function
                results = scrape_usa_swimming(config)
                
                # Verify results structure
                assert 'individual_times' in results
                assert 'event_rankings' in results
                assert 'age_group_records' in results
                assert 'top_times' in results
                assert 'stats' in results
                
                # Verify component scraper calls
                mock_scrapers = mock_all_scrapers
                individual_scraper = mock_scrapers['individual'].return_value
                ranking_scraper = mock_scrapers['rankings'].return_value
                records_scraper = mock_scrapers['records'].return_value
                top_times_scraper = mock_scrapers['top_times'].return_value
                
                # Should have called individual times scraper for each swimmer
                assert individual_scraper.scrape.call_count == len(config['swimmer_names'])
                for swimmer_name in config['swimmer_names']:
                    individual_scraper.scrape.assert_any_call({'name': swimmer_name})
                
                # Should have called event rankings scraper for each event config
                assert ranking_scraper.scrape.call_count == len(config['event_configs'])
                for event_config in config['event_configs']:
                    ranking_scraper.scrape.assert_any_call(event_config)
                
                # Should have called age group records scraper
                records_scraper.scrape.assert_called_once()
                
                # Should have called top times scraper for each top times config
                assert top_times_scraper.scrape.call_count == len(config['top_times_configs'])
                for top_times_config in config['top_times_configs']:
                    top_times_scraper.scrape.assert_any_call(top_times_config)
                
                # Check file output if save_to_file is True
                if save_to_file:
                    timestamp = '20231210150000'
                    
                    # Individual times file should exist
                    times_file = tmp_path / f'individual_times_{timestamp}.json'
                    assert times_file.exists()
                    
                    # Event rankings file should exist
                    rankings_file = tmp_path / f'event_rankings_{timestamp}.json'
                    assert rankings_file.exists()
                    
                    # Age group records file should exist
                    records_file = tmp_path / f'age_group_records_{timestamp}.json'
                    assert records_file.exists()
                    
                    # Top times file should exist
                    top_times_file = tmp_path / f'top_times_{timestamp}.json'
                    assert top_times_file.exists()
                    
                    # Stats file should exist
                    stats_file = tmp_path / f'stats_{timestamp}.json'
                    assert stats_file.exists()
                else:
                    # No files should have been created
                    assert len(list(tmp_path.iterdir())) == 0
    
    @pytest.mark.selenium
    def test_selenium_integration(self, real_webdriver):
        """Test integration with a real Selenium WebDriver.
        
        This test verifies that our WebDriver setup works correctly.
        It doesn't perform actual scraping but checks that the browser
        can be initialized and navigated.
        """
        if real_webdriver is None:
            pytest.skip("Could not create real WebDriver")
        
        try:
            # Navigate to a simple test page
            real_webdriver.get("https://www.example.com")
            
            # Verify basic page elements
            assert "Example Domain" in real_webdriver.title
            
            # Try a simple DOM interaction
            heading = real_webdriver.find_element(By.TAG_NAME, "h1")
            assert "Example Domain" in heading.text
            
            # This test just verifies that Selenium is working correctly
            # It doesn't test actual scraping logic to avoid hitting real websites
        except Exception as e:
            pytest.fail(f"Selenium integration test failed: {str(e)}")
