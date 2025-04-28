"""
Unit tests for the USA Swimming individual times scraper module.
"""

import pytest
from unittest import mock
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException

from SwimDataProject.scrapers.usa_swimming.individual_times import IndividualTimesScraper
from tests.fixtures.mock_responses import USA_SWIMMING_INDIVIDUAL_TIMES_RESULTS, USA_SWIMMING_INDIVIDUAL_TIMES_NO_RESULTS


class TestIndividualTimesScraper:
    """Tests for the IndividualTimesScraper class"""
    
    @pytest.fixture
    def scraper(self, mock_webdriver, mock_logger):
        """Create a scraper instance with mock dependencies."""
        return IndividualTimesScraper(mock_webdriver.return_value, mock_logger)
    
    def test_init(self, mock_webdriver, mock_logger):
        """Test scraper initialization."""
        scraper = IndividualTimesScraper(mock_webdriver.return_value, mock_logger)
        assert scraper.driver == mock_webdriver.return_value
        assert scraper.logger == mock_logger
    
    def test_scrape_successful(self, scraper, mock_webdriver, mock_utils):
        """Test successful scraping of individual times."""
        driver_mock = mock_webdriver.return_value
        
        # Setup mock return values
        search_params = {'name': 'John Smith', 'gender': 'Male'}
        
        # Mock the HTML content to return our test data
        driver_mock.page_source = USA_SWIMMING_INDIVIDUAL_TIMES_RESULTS
        
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
            for j in range(8):  # 8 cells per row
                cell = mock.MagicMock()
                if j == 0:  # Name
                    cell.text = "John Smith"
                elif j == 1:  # Age
                    cell.text = "16"
                elif j == 2:  # Team
                    cell.text = "FAST"
                elif j == 3:  # Event
                    cell.text = f"{100 + i*100} Free SCY"  # Different event for each row
                elif j == 4:  # Time
                    if i == 0:
                        cell.text = "49.32"
                    elif i == 1:
                        cell.text = "1:48.56"
                    else:
                        cell.text = "22.14"
                elif j == 5:  # Standard
                    cell.text = "AAA"
                elif j == 6:  # Meet Name
                    cell.text = "2023 Regional Championships"
                elif j == 7:  # Date
                    cell.text = "12/03/2023"
                cells.append(cell)
            row.find_elements.return_value = cells
            
        # Mock datetime to get predictable timestamps
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 10, 14, 30, 45)
            
            # Call the scraper
            results = scraper.scrape(search_params)
            
            # Verify the results
            assert len(results) == 3
            
            # Check first result
            assert results[0]['swimmer_name'] == "John Smith"
            assert results[0]['age'] == 16
            assert results[0]['team'] == "FAST"
            assert results[0]['event'] == "100 Free SCY"
            assert results[0]['time'] == "49.32"
            assert results[0]['time_standard'] == "AAA"
            assert results[0]['meet_name'] == "2023 Regional Championships"
            assert results[0]['meet_date'] == "12/03/2023"
            assert results[0]['meet_date_iso'] == "2023-12-03"
            assert results[0]['distance'] == 100
            assert results[0]['stroke'] == "freestyle"
            assert results[0]['course'] == "SCY"
            assert results[0]['scraped_at'] == "2023-12-10T14:30:45"
            
            # Check search form was filled correctly
            driver_mock.get.assert_called_once_with("https://data.usaswimming.org/datahub/usas/individualsearch")
            
            # Verify navigation and form submission
            driver_mock.find_element.assert_any_call(By.ID, "swimmer-name")
            driver_mock.find_element.assert_any_call(By.CSS_SELECTOR, "button[type='submit']")
    
    def test_scrape_no_results(self, scraper, mock_webdriver):
        """Test scraping when no results are found."""
        driver_mock = mock_webdriver.return_value
        
        # Setup mock return values
        search_params = {'name': 'Nonexistent Swimmer'}
        
        # Mock the HTML content to return no results
        driver_mock.page_source = USA_SWIMMING_INDIVIDUAL_TIMES_NO_RESULTS
        
        # Mock finding the no-results message
        no_results_element = mock.MagicMock()
        driver_mock.find_elements.return_value = [no_results_element]
        
        # Call the scraper
        results = scraper.scrape(search_params)
        
        # Should return empty list
        assert results == []
        
        # Verify search form was still filled
        driver_mock.get.assert_called_once_with("https://data.usaswimming.org/datahub/usas/individualsearch")
    
    def test_scrape_error_handling(self, scraper, mock_webdriver):
        """Test error handling during scraping."""
        driver_mock = mock_webdriver.return_value
        
        # Setup search params
        search_params = {'name': 'John Smith'}
        
        # Make the search form filling raise an exception
        driver_mock.find_element.side_effect = Exception("Test error")
        
        # Call the scraper - should propagate the exception
        with pytest.raises(Exception, match="Test error"):
            scraper.scrape(search_params)
    
    def test_fill_search_form(self, scraper, mock_webdriver):
        """Test form filling with different parameters."""
        driver_mock = mock_webdriver.return_value
        
        # Create mock form elements
        name_input = mock.MagicMock()
        gender_select = mock.MagicMock()
        age_input = mock.MagicMock()
        team_input = mock.MagicMock()
        lsc_select = mock.MagicMock()
        start_date_input = mock.MagicMock()
        end_date_input = mock.MagicMock()
        submit_button = mock.MagicMock()
        
        # Setup find_element to return appropriate mock elements
        driver_mock.find_element.side_effect = lambda by, value: {
            "swimmer-name": name_input,
            "swimmer-gender": gender_select,
            "swimmer-age": age_input,
            "swimmer-team": team_input,
            "swimmer-lsc": lsc_select,
            "start-date": start_date_input,
            "end-date": end_date_input,
            "button[type='submit']": submit_button
        }.get(value)
        
        # Mock Select class
        with mock.patch('SwimDataProject.scrapers.usa_swimming.individual_times.Select') as mock_select:
            mock_select.return_value = mock.MagicMock()
            
            # Call _fill_search_form with various parameters
            search_params = {
                'name': 'John Smith',
                'gender': 'Male',
                'age': 16,
                'team': 'Swim Team',
                'lsc': 'FL',
                'start_date': '01/01/2023',
                'end_date': '12/31/2023'
            }
            
            scraper._fill_search_form(search_params)
            
            # Verify all fields were filled correctly
            name_input.clear.assert_called_once()
            name_input.send_keys.assert_called_once_with('John Smith')
            
            mock_select.assert_any_call(gender_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('Male')
            
            age_input.clear.assert_called_once()
            age_input.send_keys.assert_called_once_with('16')
            
            team_input.clear.assert_called_once()
            team_input.send_keys.assert_called_once_with('Swim Team')
            
            mock_select.assert_any_call(lsc_select)
            mock_select.return_value.select_by_visible_text.assert_any_call('FL')
            
            start_date_input.clear.assert_called_once()
            start_date_input.send_keys.assert_called_once_with('01/01/2023')
            
            end_date_input.clear.assert_called_once()
            end_date_input.send_keys.assert_called_once_with('12/31/2023')
            
            submit_button.click.assert_called_once()
    
    def test_extract_results(self, scraper, mock_webdriver, mock_utils):
        """Test extracting results from result rows."""
        driver_mock = mock_webdriver.return_value
        
        # Mock finding the results table
        result_rows = [
            mock.MagicMock(),  # Row 1
            mock.MagicMock(),  # Row 2
        ]
        driver_mock.find_elements.return_value = result_rows
        
        # Setup cells for each row
        row1_cells = []
        for j in range(8):  # 8 cells
            cell = mock.MagicMock()
            if j == 0:  # Name
                cell.text = "John Smith"
            elif j == 1:  # Age
                cell.text = "16"
            elif j == 2:  # Team
                cell.text = "FAST"
            elif j == 3:  # Event
                cell.text = "100 Free SCY"
            elif j == 4:  # Time
                cell.text = "49.32"
            elif j == 5:  # Standard
                cell.text = "AAA"
            elif j == 6:  # Meet Name
                cell.text = "2023 Regional Championships"
            elif j == 7:  # Date
                cell.text = "12/03/2023"
            row1_cells.append(cell)
        
        # Row 2 - similar but with an incomplete row (missing some cells)
        row2_cells = []
        for j in range(5):  # Only 5 cells (incomplete)
            cell = mock.MagicMock()
            if j == 0:  # Name
                cell.text = "John Smith"
            elif j == 1:  # Age
                cell.text = "16"
            elif j == 2:  # Team
                cell.text = "FAST"
            elif j == 3:  # Event
                cell.text = "200 Free SCY"
            elif j == 4:  # Time
                cell.text = "1:48.56"
            row2_cells.append(cell)
        
        result_rows[0].find_elements.return_value = row1_cells
        result_rows[1].find_elements.return_value = row2_cells
        
        # Mock datetime for consistent timestamps
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 10, 14, 30, 45)
            
            # Call _extract_results
            results = scraper._extract_results()
            
            # First row should be fully populated
            assert len(results) == 1  # Row 2 doesn't have enough cells, should be skipped
            assert results[0]['swimmer_name'] == "John Smith"
            assert results[0]['age'] == 16
            assert results[0]['team'] == "FAST"
            assert results[0]['event'] == "100 Free SCY"
            assert results[0]['time'] == "49.32"
            assert results[0]['time_standard'] == "AAA"
            assert results[0]['meet_name'] == "2023 Regional Championships"
            assert results[0]['meet_date'] == "12/03/2023"
            assert results[0]['time_seconds'] == 49.32  # From mock_utils
            assert 'stroke' in results[0]  # Should have stroke from mock_utils
            assert 'distance' in results[0]  # Should have distance from mock_utils
            assert 'course' in results[0]  # Should have course from mock_utils
            assert results[0]['scraped_at'] == "2023-12-10T14:30:45"
