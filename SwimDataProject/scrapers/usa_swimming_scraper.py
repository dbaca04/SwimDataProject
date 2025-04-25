"""
USA Swimming Scraper

This module implements a scraper for USA Swimming data.
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base_scraper import BaseScraper


class USASwimmingScraper(BaseScraper):
    """
    Scraper for USA Swimming data.
    
    This scraper uses Selenium to interact with USA Swimming's data hub to 
    extract swim times, rankings, and other swimming data.
    """
    
    def __init__(self, config=None):
        """
        Initialize the USA Swimming scraper.
        
        Args:
            config (dict, optional): Configuration for the scraper
        """
        super().__init__('usa_swimming', 'https://data.usaswimming.org', config)
        self.driver = self._init_selenium_driver()
    
    def _init_selenium_driver(self):
        """
        Initialize a Selenium driver with anti-detection measures.
        
        Returns:
            webdriver.Chrome: Initialized Chrome driver
        """
        options = Options()
        
        # Set headless mode if specified in config
        if self.config.get('headless', True):
            options.add_argument('--headless')
        
        # Add arguments to make driver less detectable
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self._get_random_user_agent()}')
        
        # Disable automation flags
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to disable webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
    
    def __del__(self):
        """
        Clean up resources when the scraper is destroyed.
        """
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
    
    def scrape(self, max_states=5, swimmers_per_state=100):
        """
        Main scraping method for USA Swimming data.
        
        Args:
            max_states (int, optional): Maximum number of states to scrape
            swimmers_per_state (int, optional): Target number of swimmers per state
        
        Returns:
            list: Scraped data
        """
        self.logger.info("Starting scrape of USA Swimming data")
        
        # Define states to scrape (prioritizing larger swimming programs as mentioned in docs)
        priority_states = ['California', 'Texas', 'New Mexico', 'Arizona', 'Colorado', 'Nevada']
        states_to_scrape = priority_states[:max_states]
        
        all_results = []
        
        # Scrape each state
        for state in states_to_scrape:
            self.logger.info(f"Scraping data for state: {state}")
            
            # Create search parameters
            search_params = {
                'state': state,
                # Start with recent data
                'start_date': '01/01/2024',  # Adjust date as needed
                # We don't set specific names to get a broad range of swimmers
            }
            
            # Scrape times for the state
            state_results = self.scrape_individual_times(search_params, max_pages=10)
            
            self.logger.info(f"Found {len(state_results)} results for {state}")
            all_results.extend(state_results)
            
            # Break if we've reached our target
            if len(all_results) >= max_states * swimmers_per_state:
                self.logger.info(f"Reached target of {max_states * swimmers_per_state} records, stopping early")
                break
            
            # Respect rate limits between states
            self.rate_limit(5, 10)
        
        # Try additional search strategies if we didn't get enough data
        if len(all_results) < max_states * swimmers_per_state / 2:
            self.logger.info("Not enough data collected, trying additional search strategies")
            
            # Try searching for top events
            popular_events = ['50 Freestyle', '100 Freestyle', '100 Butterfly', '200 IM']
            
            for event in popular_events:
                search_params = {
                    'event': event,
                    'start_date': '01/01/2024',  # Adjust date as needed
                }
                
                event_results = self.scrape_individual_times(search_params, max_pages=5)
                
                self.logger.info(f"Found {len(event_results)} results for event {event}")
                all_results.extend(event_results)
                
                # Respect rate limits between searches
                self.rate_limit(5, 10)
                
                # Break if we've reached our target
                if len(all_results) >= max_states * swimmers_per_state:
                    break
        
        # Save the data to the database
        records_saved = self.save_data(all_results)
        
        self.logger.info(f"Completed scrape, found {len(all_results)} records, saved {records_saved} to database")
        return all_results
    
    def scrape_by_event(self, event_name, gender=None, age_group=None, max_pages=5):
        """
        Scrape data for a specific event, optionally filtered by gender and age group.
        
        Args:
            event_name (str): Event name (e.g., '100 Freestyle')
            gender (str, optional): 'M' for male, 'F' for female
            age_group (tuple, optional): Tuple of (min_age, max_age)
            max_pages (int, optional): Maximum number of result pages to scrape
        
        Returns:
            list: List of swim time data for the specified event
        """
        self.logger.info(f"Searching for event: {event_name}")
        
        search_params = {
            'event': event_name
        }
        
        if gender:
            search_params['gender'] = gender
        
        if age_group and len(age_group) == 2:
            search_params['min_age'] = age_group[0]
            search_params['max_age'] = age_group[1]
        
        results = self.scrape_individual_times(search_params, max_pages)
        
        self.logger.info(f"Found {len(results)} results for event {event_name}")
        return results
    
    def scrape_by_swimmer_name(self, first_name, last_name, max_pages=3):
        """
        Scrape data for a specific swimmer by name.
        
        Args:
            first_name (str): Swimmer's first name
            last_name (str): Swimmer's last name
            max_pages (int, optional): Maximum number of result pages to scrape
        
        Returns:
            list: List of swim time data for the specified swimmer
        """
        self.logger.info(f"Searching for swimmer: {first_name} {last_name}")
        
        search_params = {
            'first_name': first_name,
            'last_name': last_name
        }
        
        results = self.scrape_individual_times(search_params, max_pages)
        
        self.logger.info(f"Found {len(results)} results for {first_name} {last_name}")
        return results
    
    def scrape_individual_times(self, search_params, max_pages=5):
        """
        Scrape individual times using search parameters.
        
        Args:
            search_params (dict): Parameters to search for times
            max_pages (int, optional): Maximum number of result pages to scrape
            
        Returns:
            list: List of times data
        """
        all_results = []
        
        try:
            # Navigate to search page
            self.driver.get(f"{self.base_url}/datahub/usas/individualsearch")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "swimmer-search-form"))
            )
            
            # Fill in search form
            self._fill_search_form(search_params)
            
            # Extract results from first page
            results = self._extract_results()
            all_results.extend(results)
            
            # Check if there are additional pages
            page_count = 1
            
            while page_count < max_pages:
                # Check if there's a next page button
                next_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Next') or contains(@class, 'next-page')]")
                
                if not next_buttons or len(next_buttons) == 0:
                    # No more pages
                    break
                
                # Click next page
                next_buttons[0].click()
                
                # Wait for results to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "search-results"))
                )
                
                # Add a short delay to ensure results are fully loaded
                self.rate_limit(1, 3)
                
                # Extract results from this page
                page_results = self._extract_results()
                
                if not page_results or len(page_results) == 0:
                    # No more results
                    break
                
                # Add these results to all results
                all_results.extend(page_results)
                
                # Increment page count
                page_count += 1
                
                self.logger.info(f"Scraped page {page_count}, found {len(page_results)} results")
            
            self.logger.info(f"Scraped {page_count} pages, found {len(all_results)} total results")
            return all_results
            
        except Exception as e:
            self.logger.error(f"Error scraping individual times: {str(e)}")
            return all_results  # Return any results we got before the error
    
    def _fill_search_form(self, search_params):
        """
        Fill in the search form with provided parameters.
        
        Args:
            search_params (dict): Search parameters
        """
        try:
            # Wait for the form to be fully loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "swimmer-search-form"))
            )
            
            # Fill in the form based on search parameters
            # First name
            if 'first_name' in search_params:
                first_name_input = self.driver.find_element(By.ID, "search-first-name")
                first_name_input.clear()
                first_name_input.send_keys(search_params['first_name'])
            
            # Last name
            if 'last_name' in search_params:
                last_name_input = self.driver.find_element(By.ID, "search-last-name")
                last_name_input.clear()
                last_name_input.send_keys(search_params['last_name'])
            
            # Gender
            if 'gender' in search_params:
                gender_select = self.driver.find_element(By.ID, "search-gender")
                if search_params['gender'].upper() == 'M':
                    gender_select.find_element(By.XPATH, "//option[text()='Male']").click()
                elif search_params['gender'].upper() == 'F':
                    gender_select.find_element(By.XPATH, "//option[text()='Female']").click()
            
            # Age range
            if 'min_age' in search_params:
                min_age_input = self.driver.find_element(By.ID, "search-min-age")
                min_age_input.clear()
                min_age_input.send_keys(str(search_params['min_age']))
            
            if 'max_age' in search_params:
                max_age_input = self.driver.find_element(By.ID, "search-max-age")
                max_age_input.clear()
                max_age_input.send_keys(str(search_params['max_age']))
            
            # Team name
            if 'team' in search_params:
                team_input = self.driver.find_element(By.ID, "search-team")
                team_input.clear()
                team_input.send_keys(search_params['team'])
            
            # State
            if 'state' in search_params:
                state_select = self.driver.find_element(By.ID, "search-state")
                state_option = f"//option[text()='{search_params['state']}']"
                state_select.find_element(By.XPATH, state_option).click()
            
            # Time range
            if 'start_date' in search_params:
                start_date_input = self.driver.find_element(By.ID, "search-start-date")
                start_date_input.clear()
                start_date_input.send_keys(search_params['start_date'])
            
            if 'end_date' in search_params:
                end_date_input = self.driver.find_element(By.ID, "search-end-date")
                end_date_input.clear()
                end_date_input.send_keys(search_params['end_date'])
            
            # Event
            if 'event' in search_params:
                event_select = self.driver.find_element(By.ID, "search-event")
                event_option = f"//option[contains(text(), '{search_params['event']}')]"
                event_select.find_element(By.XPATH, event_option).click()
            
            # Course
            if 'course' in search_params:
                course_select = self.driver.find_element(By.ID, "search-course")
                course_option = f"//option[text()='{search_params['course']}']"
                course_select.find_element(By.XPATH, course_option).click()
            
            # Submit the form
            search_button = self.driver.find_element(By.ID, "search-submit")
            search_button.click()
            
            # Wait for results to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "search-results"))
            )
            
            # Add a short delay to ensure results are fully loaded
            self.rate_limit(2, 4)
            
        except Exception as e:
            self.logger.error(f"Error filling search form: {str(e)}")
            raise
    
    def _extract_results(self):
        """
        Extract results from the page after search.
        
        Returns:
            list: Extracted results as dictionaries with swimmer and time data
        """
        results = []
        
        try:
            # Check if results are present
            results_table = self.driver.find_element(By.ID, "search-results")
            
            # Check if we have a "no results" message
            no_results_elements = self.driver.find_elements(By.CLASS_NAME, "no-results")
            if no_results_elements and len(no_results_elements) > 0:
                self.logger.info("No results found for this search")
                return []
            
            # Get all result rows (skip header row)
            rows = results_table.find_elements(By.TAG_NAME, "tr")[1:]
            
            for row in rows:
                try:
                    # Get cells from row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 8:  # Make sure we have enough cells
                        continue
                    
                    # Extract data from each cell
                    swimmer_name = cells[0].text.strip()
                    
                    # Split name into first and last
                    name_parts = swimmer_name.split(',')
                    last_name = name_parts[0].strip() if len(name_parts) > 0 else ""
                    first_name = name_parts[1].strip() if len(name_parts) > 1 else ""
                    
                    age = int(cells[1].text.strip()) if cells[1].text.strip().isdigit() else None
                    team = cells[2].text.strip()
                    
                    # Get the meet information
                    meet_name = cells[3].text.strip()
                    meet_date_str = cells[4].text.strip()
                    
                    # Get the event information
                    event = cells[5].text.strip()
                    
                    # Parse stroke and distance from event
                    event_parts = event.split()
                    distance = int(''.join(filter(str.isdigit, event_parts[0]))) if len(event_parts) > 0 else None
                    stroke = ' '.join(event_parts[1:]) if len(event_parts) > 1 else ""
                    
                    # Get time information
                    time_formatted = cells[6].text.strip()
                    
                    # Convert time to seconds
                    time_seconds = self._convert_time_to_seconds(time_formatted)
                    
                    # Course (SCY, SCM, LCM)
                    course = cells[7].text.strip()
                    
                    # Build result dictionary
                    result = {
                        'swimmer': {
                            'first_name': first_name,
                            'last_name': last_name,
                            'full_name': f"{first_name} {last_name}",
                            'age': age,
                            'team': team
                        },
                        'meet': {
                            'name': meet_name,
                            'date': meet_date_str
                        },
                        'event': {
                            'name': event,
                            'distance': distance,
                            'stroke': stroke,
                            'course': course
                        },
                        'time': {
                            'formatted': time_formatted,
                            'seconds': time_seconds
                        },
                        'source': 'usa_swimming',
                        'source_url': self.driver.current_url
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting data from row: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting results: {str(e)}")
            return []
    
    def _convert_time_to_seconds(self, time_str):
        """
        Convert a time string to seconds.
        
        Args:
            time_str (str): Time string in format MM:SS.ss or SS.ss
            
        Returns:
            float: Time in seconds
        """
        time_str = time_str.strip()
        
        try:
            # Handle different time formats
            if ':' in time_str:
                # Format: MM:SS.ss
                parts = time_str.split(':')
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                # Format: SS.ss
                return float(time_str)
        except Exception as e:
            self.logger.warning(f"Error converting time '{time_str}' to seconds: {str(e)}")
            return None
    
    def save_data(self, data):
        """
        Save scraped data to database.
        
        Args:
            data (list): Data to save
            
        Returns:
            int: Number of records saved
        """
        # Implementation details for saving data
        # This is a placeholder for actual implementation
        return len(data)
