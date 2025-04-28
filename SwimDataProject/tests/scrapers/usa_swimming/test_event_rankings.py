"""
Unit tests for the USA Swimming event rankings scraper module.
"""

import pytest
from unittest import mock
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException

from SwimDataProject.scrapers.usa_swimming.event_rankings import EventRankingsScraper
from tests.fixtures.mock_responses import USA_SWIMMING_EVENT_RANKINGS_RESULTS


class TestEventRankingsScraper:
    """Tests for the EventRankingsScraper class"""
    
    @pytest.fixture
    def scraper(self, mock_webdriver, mock_logger):
        """Create a scraper instance with mock dependencies."""
        return EventRankingsScraper(mock_webdriver.return_value, mock_logger)
    
    def test_init(self, mock_webdriver, mock_logger):
        """Test scraper initialization."""
        scraper = EventRankingsScraper(mock_webdriver.return_value, mock_logger)
        assert scraper.driver == mock_webdriver.return_value
        assert scraper.logger == mock_logger
    
    def test_scrape_successful(self, scraper, mock_webdriver, mock_utils):
        """Test successful scraping of event rankings."""
        driver_mock = mock_webdriver.return_value
        
        # Setup mock return values
        event_config = {
            'event': '50 Freestyle',
            'course': 'SCY',
            'age_group': '17-18',
            'gender': 'Male'
        }
        
        # Mock the HTML content
        driver_mock.page_source = USA_SWIMMING_EVENT_RANKINGS_RESULTS
        
        # Mock finding the results table
        result_rows = [
            mock.MagicMock(),  # Row 1
            mock.MagicMock(),  # Row 2
            mock.MagicMock(),  # Row 3
        ]
        driver_mock.find_elements.return_value = result_rows
        
        # Setup cells for each row
        for i, row in enumerate(result_rows):
            cells = []
            for j in range(7):  # 7 cells per row
                cell = mock.MagicMock()
                if j == 0:  # Rank
                    cell.text = str(i + 1)
                elif j == 1:  # Swimmer Name
                    if i == 0:
                        cell.text = "Alex Johnson"
                    elif i == 1:
                        cell.text = "Michael Williams"
                    else:
                        cell.text = "Chris Davis"
                elif j == 2:  # Age
                    cell.text = "17"
                elif j == 3:  # Team
                    if i == 0:
                        cell.text = "SWIM"
                    elif i == 1:
                        cell.text = "RACE"
                    else:
                        cell.text = "DASH"
                elif j == 4:  # Time
                    if i == 0:
                        cell.text = "20.14"
                    elif i == 1:
                        cell.text = "20.32"
                    else:
                        cell.text = "20.45"
                elif j == 5:  # Meet Name
                    if i == 0:
                        cell.text = "2023 National Championships"
                    elif i == 1:
                        cell.text = "2023 Regional Championships"
                    else:
                        cell.text = "2023 State Meet"
                elif j == 6:  # Date
                    if i == 0:
                        cell.text = "03/15/2023"
                    elif i == 1:
                        cell.text = "02/20/2023"
                    else:
                        cell.text = "01/10/2023"
                cells.append(cell)
            row.find_elements.return_value = cells
            
        # Mock datetime to get predictable timestamps
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 10, 14, 32, 10)
            
            # Call the scraper
            results = scraper.scrape(event_config)
            
            # Verify the results
            assert len(results) == 3
            
            # Check first result
            assert results[0]['rank'] == 1
            assert results[0]['swimmer_name'] == "Alex Johnson"
            assert results[0]['age'] == 17
            assert results[0]['team'] == "SWIM"
            assert results[0]['time'] == "20.14"
            assert results[0]['time_seconds'] == 20.14  # From mock_utils
            assert results[0]['meet_name'] == "2023 National Championships"
            assert results[0]['meet_date'] == "03/15/2023"
            assert results[0]['meet_date_iso'] == "2023-12-03"  # From mock_utils
            assert results[0]['event'] == "50 Freestyle"
            assert results[0]['gender'] == "Male"
            assert results[0]['course'] == "SCY"
            assert results[0]['scraped_at'] == "2023-12-10T14:32:10"
            
            # Verify navigation and form submission
            driver_mock.get.assert_called_once_with("https://data.usaswimming.org/datahub/usas/timeseventrank")
    
    def test_scrape_no_results(self, scraper, mock_webdriver):
        """Test scraping when no results are found."""
        driver_mock = mock_webdriver.return_value
        
        # Setup mock return values
        event_config = {
            'event': '50 Freestyle',
            'course': 'SCY',
            'age_group': '17-18',
            'gender': 'Male'
        }
        
        # Mock finding no result rows
        driver_mock.find_elements.return_value = []
        
        # Call the scraper
        results = scraper.scrape(event_config)
        
        # Should return empty list
        assert results == []
        
        # Verify search form was still filled
        driver_mock.get.assert_called_once_with("https://data.usaswimming.org/datahub/usas/timeseventrank")
    
    def test_fill_ranking_form(self, scraper, mock_webdriver):
        """Test form filling with different parameters."""
        driver_mock = mock_webdriver.return_value
        
        # Create mock form elements
        event_select = mock.MagicMock()
        course_select = mock.MagicMock()
        age_group_select = mock.MagicMock()
        gender_select = mock.MagicMock()
        start_date_input = mock.MagicMock()
        end_date_input = mock.MagicMock()
        submit_button = mock.MagicMock()
        
        # Setup find_element to return appropriate mock elements
        driver_mock.find_element.side_effect = lambda by, value: {
            "event-name": event_select,
            "course-type": course_select,
            "age-group": age_group_select,
            "gender": gender_select,
            "start-date": start_date_input,
            "end-date": end_date_input,
            "button[type='submit']": submit_button
        }.get(value)
        
        # Mock Select class
        with mock.patch('SwimDataProject.scrapers.usa_swimming.event_rankings.Select') as mock_select:
            mock_select.return_value = mock.MagicMock()
            
            # Call _fill_ranking_form with various parameters
            event_config = {
                'event': '50 Freestyle',
                'course': 'SCY',
                'age_group': '17-18',
                'gender': 'Male',
                'start_date': '01/01/2023',
                'end_date': '12/31/2023'
            }
            
            scraper._fill_ranking_form(event_config)
            
            # Verify all fields were filled correctly
            mock_select.assert_any_call(event_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('50 Freestyle')
            
            mock_select.assert_any_call(course_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('SCY')
            
            mock_select.assert_any_call(age_group_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('17-18')
            
            mock_select.assert_any_call(gender_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('Male')
            
            start_date_input.clear.assert_called_once()
            start_date_input.send_keys.assert_called_once_with('01/01/2023')
            
            end_date_input.clear.assert_called_once()
            end_date_input.send_keys.assert_called_once_with('12/31/2023')
            
            submit_button.click.assert_called_once()
    
    def test_extract_ranking_results(self, scraper, mock_webdriver, mock_utils):
        """Test extracting results from ranking table."""
        driver_mock = mock_webdriver.return_value
        
        # Mock finding the results table
        result_rows = [
            mock.MagicMock(),  # Row 1
            mock.MagicMock(),  # Row 2
        ]
        driver_mock.find_elements.return_value = result_rows
        
        # Setup cells for each row
        row1_cells = []
        for j in range(7):  # 7 cells
            cell = mock.MagicMock()
            if j == 0:  # Rank
                cell.text = "1"
            elif j == 1:  # Swimmer Name
                cell.text = "Alex Johnson"
            elif j == 2:  # Age
                cell.text = "17"
            elif j == 3:  # Team
                cell.text = "SWIM"
            elif j == 4:  # Time
                cell.text = "20.14"
            elif j == 5:  # Meet Name
                cell.text = "2023 National Championships"
            elif j == 6:  # Date
                cell.text = "03/15/2023"
            row1_cells.append(cell)
        
        # Row 2 - similar but with an incomplete row (missing some cells)
        row2_cells = []
        for j in range(4):  # Only 4 cells (incomplete)
            cell = mock.MagicMock()
            if j == 0:  # Rank
                cell.text = "2"
            elif j == 1:  # Swimmer Name
                cell.text = "Michael Williams"
            elif j == 2:  # Age
                cell.text = "17"
            elif j == 3:  # Team
                cell.text = "RACE"
            row2_cells.append(cell)
        
        result_rows[0].find_elements.return_value = row1_cells
        result_rows[1].find_elements.return_value = row2_cells
        
        # Set event config
        event_config = {
            'event': '50 Freestyle',
            'course': 'SCY',
            'gender': 'Male'
        }
        
        # Mock datetime for consistent timestamps
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 10, 14, 32, 10)
            
            # Call _extract_ranking_results
            results = scraper._extract_ranking_results(event_config)
            
            # First row should be fully populated
            assert len(results) == 1  # Row 2 doesn't have enough cells, should be skipped
            assert results[0]['rank'] == 1
            assert results[0]['swimmer_name'] == "Alex Johnson"
            assert results[0]['age'] == 17
            assert results[0]['team'] == "SWIM"
            assert results[0]['time'] == "20.14"
            assert results[0]['time_seconds'] == 20.14  # From mock_utils
            assert results[0]['meet_name'] == "2023 National Championships"
            assert results[0]['meet_date'] == "03/15/2023"
            assert results[0]['meet_date_iso'] == "2023-12-03"  # From mock_utils
            assert results[0]['event'] == "50 Freestyle"
            assert results[0]['gender'] == "Male"
            assert results[0]['course'] == "SCY"
            assert results[0]['scraped_at'] == "2023-12-10T14:32:10"
