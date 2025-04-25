"""
NISCA Scraper

This module implements a scraper for NISCA (National Interscholastic Swim Coaches Association) data.
"""
import time
import re
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base_scraper import BaseScraper


class NIScAScraper(BaseScraper):
    """
    Scraper for NISCA data.
    
    This scraper retrieves national high school records and All-America lists
    from the National Interscholastic Swim Coaches Association website.
    """
    
    def __init__(self, config=None):
        """
        Initialize the NISCA scraper.
        
        Args:
            config (dict, optional): Configuration for the scraper
        """
        super().__init__('nisca', 'https://niscaonline.org', config)
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
    
    def scrape(self):
        """
        Main scraping method for NISCA data.
        
        Returns:
            dict: Dictionary containing national records and All-America lists
        """
        self.logger.info("Starting scrape of NISCA data")
        
        all_data = {
            'records': {},
            'all_america': {}
        }
        
        # Scrape national records
        male_records = self.scrape_records(gender='male')
        female_records = self.scrape_records(gender='female')
        
        all_data['records']['male'] = male_records
        all_data['records']['female'] = female_records
        
        # Scrape All-America lists
        all_america = self.scrape_all_america()
        all_data['all_america'] = all_america
        
        self.logger.info(f"Completed NISCA scrape, found {len(male_records) + len(female_records)} records")
        return all_data
    
    def scrape_records(self, gender='male'):
        """
        Scrape national high school records.
        
        Args:
            gender (str): 'male' or 'female'
            
        Returns:
            dict: Dictionary of event records
        """
        gender_url = 'male-records' if gender == 'male' else 'female-records'
        url = f"{self.base_url}/index.php/records/{gender_url}"
        
        self.logger.info(f"Scraping {gender} records from {url}")
        
        try:
            # Navigate to records page
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Get the page source and create a BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract records from tables
            records = self._extract_records(soup, gender)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Error scraping {gender} records: {str(e)}")
            return {}
    
    def _extract_records(self, soup, gender):
        """
        Extract records from the HTML.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the records page
            gender (str): 'male' or 'female'
            
        Returns:
            dict: Dictionary of event records
        """
        records = {}
        
        try:
            # Find record tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this is a records table
                if 'National Record' in table.text:
                    # Extract records from this table
                    self._extract_table_records(table, records, gender)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Error extracting records: {str(e)}")
            return {}
    
    def _extract_table_records(self, table, records, gender):
        """
        Extract records from a single table.
        
        Args:
            table (BeautifulSoup.Tag): Table element
            records (dict): Dictionary to store records
            gender (str): 'male' or 'female'
        """
        try:
            # Get the header row to determine the columns
            headers = table.find_all('th')
            
            # Get the event name from the table caption or first row
            event_name = "Unknown Event"
            if table.find('caption'):
                event_name = table.find('caption').text.strip()
            else:
                # Try to determine event from first row
                first_row = table.find('tr')
                if first_row:
                    event_name = first_row.text.strip()
            
            # Clean up event name
            event_name = self._clean_event_name(event_name)
            
            # Get data rows
            rows = table.find_all('tr')
            
            # Skip header row(s)
            data_rows = rows[1:] if len(rows) > 1 else []
            
            for row in data_rows:
                cells = row.find_all('td')
                
                if len(cells) >= 4:  # Ensure we have enough cells
                    record_type = "Unknown"
                    if cells[0].text.strip():
                        record_type = cells[0].text.strip()
                    
                    record_data = {
                        'event': event_name,
                        'type': record_type,
                        'time': cells[1].text.strip(),
                        'name': cells[2].text.strip(),
                        'school': cells[3].text.strip(),
                        'year': cells[4].text.strip() if len(cells) > 4 else "",
                        'gender': gender
                    }
                    
                    # Add to records dictionary
                    key = f"{event_name}-{record_type}"
                    records[key] = record_data
        
        except Exception as e:
            self.logger.error(f"Error extracting records from table: {str(e)}")
    
    def _clean_event_name(self, event_name):
        """
        Clean up event name for consistency.
        
        Args:
            event_name (str): Raw event name
            
        Returns:
            str: Cleaned event name
        """
        # Remove any "National Record" or similar text
        event_name = re.sub(r'National Record', '', event_name, flags=re.IGNORECASE).strip()
        
        # Remove any "Boys" or "Girls" indicators
        event_name = re.sub(r'Boys|Girls', '', event_name, flags=re.IGNORECASE).strip()
        
        # Standardize common event names
        event_maps = {
            '50 Freestyle': '50 Freestyle',
            '50 Free': '50 Freestyle',
            '50 Yard Freestyle': '50 Freestyle',
            '100 Freestyle': '100 Freestyle',
            '100 Free': '100 Freestyle',
            '200 Freestyle': '200 Freestyle',
            '200 Free': '200 Freestyle',
            '500 Freestyle': '500 Freestyle',
            '500 Free': '500 Freestyle',
            '100 Butterfly': '100 Butterfly',
            '100 Fly': '100 Butterfly',
            '100 Backstroke': '100 Backstroke',
            '100 Back': '100 Backstroke',
            '100 Breaststroke': '100 Breaststroke',
            '100 Breast': '100 Breaststroke',
            '200 Individual Medley': '200 Individual Medley',
            '200 IM': '200 Individual Medley',
            '200 Medley Relay': '200 Medley Relay',
            '400 Freestyle Relay': '400 Freestyle Relay',
            '400 Free Relay': '400 Freestyle Relay',
            '200 Freestyle Relay': '200 Freestyle Relay',
            '200 Free Relay': '200 Freestyle Relay'
        }
        
        # Check for matches in our map
        for key, value in event_maps.items():
            if key.lower() in event_name.lower():
                return value
        
        # If no match, return the cleaned string
        return event_name.strip()
    
    def scrape_all_america(self):
        """
        Scrape All-America lists.
        
        Returns:
            dict: Dictionary of All-America lists by year and category
        """
        url = f"{self.base_url}/index.php/award-programs/all-america-swimming"
        
        self.logger.info(f"Scraping All-America lists from {url}")
        
        try:
            # Navigate to All-America page
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Get the page source and create a BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract links to All-America lists
            all_america_data = self._extract_all_america_links(soup)
            
            # For each link, scrape the list
            for year, categories in all_america_data.items():
                for category, url in categories.items():
                    self.logger.info(f"Scraping {year} {category} All-America list")
                    
                    # Allow a small delay between requests
                    self.rate_limit(1, 2)
                    
                    try:
                        # Navigate to the list page
                        self.driver.get(url)
                        
                        # Wait for page to load
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "table"))
                        )
                        
                        # Get the page source and create a BeautifulSoup object
                        list_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        
                        # Extract the All-America list
                        all_america_lists = self._extract_all_america_list(list_soup, year, category)
                        
                        # Add to the data dictionary
                        all_america_data[year][category] = all_america_lists
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping {year} {category} All-America list: {str(e)}")
            
            return all_america_data
            
        except Exception as e:
            self.logger.error(f"Error scraping All-America lists: {str(e)}")
            return {}
    
    def _extract_all_america_links(self, soup):
        """
        Extract links to All-America lists.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the All-America page
            
        Returns:
            dict: Dictionary of All-America list links by year and category
        """
        all_america_data = {}
        
        try:
            # Find links to All-America lists
            links = soup.find_all('a')
            
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()
                
                # Look for links to All-America lists
                if 'all-america' in href.lower() and text:
                    # Try to extract year and category
                    year_match = re.search(r'20\d{2}[-\s]20\d{2}', text)
                    year = year_match.group(0) if year_match else "Unknown"
                    
                    # Determine category (boys, girls, etc.)
                    category = "Unknown"
                    if 'boys' in text.lower():
                        category = "Boys"
                    elif 'girls' in text.lower():
                        category = "Girls"
                    
                    # Add to data dictionary
                    if year not in all_america_data:
                        all_america_data[year] = {}
                    
                    # Create full URL if it's a relative link
                    if href.startswith('/') or not href.startswith('http'):
                        href = f"{self.base_url}{href if href.startswith('/') else '/' + href}"
                    
                    all_america_data[year][category] = href
            
            return all_america_data
            
        except Exception as e:
            self.logger.error(f"Error extracting All-America links: {str(e)}")
            return {}
    
    def _extract_all_america_list(self, soup, year, category):
        """
        Extract All-America list data.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the All-America list page
            year (str): Year of the list
            category (str): Category (Boys, Girls)
            
        Returns:
            dict: Dictionary of All-America list data by event
        """
        all_america_list = {}
        
        try:
            # Find tables containing All-America lists
            tables = soup.find_all('table')
            
            for table in tables:
                # Extract event name
                event_name = "Unknown Event"
                if table.find('caption'):
                    event_name = table.find('caption').text.strip()
                elif table.find('th'):
                    # Try to determine event from header row
                    header_text = table.find('th').text.strip()
                    event_name = header_text
                
                # Clean up event name
                event_name = self._clean_event_name(event_name)
                
                # Extract swimmers in this event
                swimmers = self._extract_all_america_swimmers(table, event_name, category)
                
                # Add to list dictionary
                if swimmers:
                    all_america_list[event_name] = swimmers
            
            return all_america_list
            
        except Exception as e:
            self.logger.error(f"Error extracting All-America list: {str(e)}")
            return {}
    
    def _extract_all_america_swimmers(self, table, event_name, category):
        """
        Extract swimmers from All-America list table.
        
        Args:
            table (BeautifulSoup.Tag): Table element
            event_name (str): Event name
            category (str): Category (Boys, Girls)
            
        Returns:
            list: List of swimmer dictionaries
        """
        swimmers = []
        
        try:
            # Find column indices
            header_row = table.find('tr')
            headers = [th.text.strip().lower() for th in header_row.find_all('th')] if header_row else []
            
            # Map column indices
            name_idx = next((i for i, h in enumerate(headers) if 'name' in h), None)
            school_idx = next((i for i, h in enumerate(headers) if 'school' in h), None)
            time_idx = next((i for i, h in enumerate(headers) if 'time' in h), None)
            year_idx = next((i for i, h in enumerate(headers) if 'year' in h or 'grade' in h), None)
            state_idx = next((i for i, h in enumerate(headers) if 'state' in h), None)
            
            # Get data rows
            rows = table.find_all('tr')
            
            # Skip header row
            data_rows = rows[1:] if len(rows) > 1 else []
            
            for row in data_rows:
                cells = row.find_all('td')
                
                if len(cells) >= 3:  # Ensure we have enough cells
                    swimmer_data = {
                        'event': event_name,
                        'category': category,
                        'name': cells[name_idx].text.strip() if name_idx is not None and name_idx < len(cells) else "",
                        'school': cells[school_idx].text.strip() if school_idx is not None and school_idx < len(cells) else "",
                        'time': cells[time_idx].text.strip() if time_idx is not None and time_idx < len(cells) else "",
                        'year': cells[year_idx].text.strip() if year_idx is not None and year_idx < len(cells) else "",
                        'state': cells[state_idx].text.strip() if state_idx is not None and state_idx < len(cells) else ""
                    }
                    
                    swimmers.append(swimmer_data)
            
            return swimmers
            
        except Exception as e:
            self.logger.error(f"Error extracting All-America swimmers: {str(e)}")
            return []
    
    def save_data(self, data):
        """
        Save scraped data to database.
        
        Args:
            data (dict): Data to save
            
        Returns:
            int: Number of records saved
        """
        from database.database import db_session
        from database.models import (
            Swimmer, SwimmerAlias, Team, TeamAlias, Event, EventAlias, 
            Record, TimeStandard, DataSource
        )
        from datetime import datetime
        
        saved_count = 0
        
        with db_session() as session:
            # First, ensure we have a data source
            data_source = session.query(DataSource).filter(
                DataSource.name == 'nisca'
            ).first()
            
            if not data_source:
                data_source = DataSource(
                    name='nisca',
                    url='https://niscaonline.org',
                    description='National Interscholastic Swim Coaches Association',
                    last_scraped=datetime.now(),
                    scrape_frequency='monthly',
                    active=True
                )
                session.add(data_source)
                session.flush()
            else:
                # Update last scraped timestamp
                data_source.last_scraped = datetime.now()
            
            # Save records
            if 'records' in data:
                for gender, records in data['records'].items():
                    for record_key, record_data in records.items():
                        try:
                            # Find or create event
                            event_name = record_data['event']
                            
                            # Parse event details
                            event_details = self._parse_event_name(event_name)
                            
                            event = session.query(Event).filter(
                                Event.name == event_name,
                                Event.course == 'SCY'  # NISCA records are in yards
                            ).first()
                            
                            if not event:
                                event = Event(
                                    name=event_name,
                                    distance=event_details['distance'],
                                    stroke=event_details['stroke'],
                                    course='SCY',
                                    is_relay=event_details['is_relay'],
                                    standard_name=event_name
                                )
                                session.add(event)
                                session.flush()
                            
                            # Parse time
                            time_seconds = self._convert_time_to_seconds(record_data['time'])
                            
                            # Parse name
                            swimmer_name = record_data['name']
                            
                            # Create or update record
                            gender_code = 'M' if gender == 'male' else 'F'
                            
                            record = session.query(Record).filter(
                                Record.event_id == event.id,
                                Record.record_type == 'national_high_school',
                                Record.gender == gender_code,
                                Record.is_current == True
                            ).first()
                            
                            if not record:
                                record = Record(
                                    event_id=event.id,
                                    record_type='national_high_school',
                                    gender=gender_code,
                                    swimmer_name=swimmer_name,
                                    team_name=record_data['school'],
                                    time_seconds=time_seconds,
                                    time_formatted=record_data['time'],
                                    record_date=None,  # We don't have a specific date
                                    source='nisca',
                                    is_current=True
                                )
                                session.add(record)
                                saved_count += 1
                            else:
                                # Update if the time is faster
                                if time_seconds < record.time_seconds:
                                    record.swimmer_name = swimmer_name
                                    record.team_name = record_data['school']
                                    record.time_seconds = time_seconds
                                    record.time_formatted = record_data['time']
                                    saved_count += 1
                        
                        except Exception as e:
                            self.logger.error(f"Error saving record: {str(e)}")
                            continue
            
            # Save All-America times as time standards
            if 'all_america' in data:
                for year, categories in data['all_america'].items():
                    for category, events in categories.items():
                        if isinstance(events, dict):  # Only process if it's a dictionary of events
                            for event_name, swimmers in events.items():
                                try:
                                    # Find or create event
                                    event_details = self._parse_event_name(event_name)
                                    
                                    event = session.query(Event).filter(
                                        Event.name == event_name,
                                        Event.course == 'SCY'  # All-America times are in yards
                                    ).first()
                                    
                                    if not event:
                                        event = Event(
                                            name=event_name,
                                            distance=event_details['distance'],
                                            stroke=event_details['stroke'],
                                            course='SCY',
                                            is_relay=event_details['is_relay'],
                                            standard_name=event_name
                                        )
                                        session.add(event)
                                        session.flush()
                                    
                                    # Get gender code
                                    gender_code = 'M' if category == 'Boys' else 'F'
                                    
                                    # Extract season from year (e.g., "2022-2023")
                                    season = year
                                    
                                    # Find the fastest time as the standard
                                    if swimmers and isinstance(swimmers, list):
                                        fastest_time = None
                                        fastest_time_seconds = float('inf')
                                        
                                        for swimmer in swimmers:
                                            if 'time' in swimmer:
                                                time_seconds = self._convert_time_to_seconds(swimmer['time'])
                                                if time_seconds and time_seconds < fastest_time_seconds:
                                                    fastest_time = swimmer['time']
                                                    fastest_time_seconds = time_seconds
                                        
                                        if fastest_time and fastest_time_seconds < float('inf'):
                                            # Save as time standard
                                            standard = session.query(TimeStandard).filter(
                                                TimeStandard.event_id == event.id,
                                                TimeStandard.standard_name == 'All-America',
                                                TimeStandard.gender == gender_code,
                                                TimeStandard.season == season
                                            ).first()
                                            
                                            if not standard:
                                                standard = TimeStandard(
                                                    event_id=event.id,
                                                    standard_name='All-America',
                                                    gender=gender_code,
                                                    age_group='High School',
                                                    time_seconds=fastest_time_seconds,
                                                    time_formatted=fastest_time,
                                                    season=season,
                                                    source='nisca'
                                                )
                                                session.add(standard)
                                                saved_count += 1
                                            else:
                                                # Update if the time is different
                                                if fastest_time_seconds != standard.time_seconds:
                                                    standard.time_seconds = fastest_time_seconds
                                                    standard.time_formatted = fastest_time
                                                    saved_count += 1
                                
                                except Exception as e:
                                    self.logger.error(f"Error saving All-America standard: {str(e)}")
                                    continue
        
        return saved_count
    
    def _parse_event_name(self, event_name):
        """
        Parse event name to extract details.
        
        Args:
            event_name (str): Event name
            
        Returns:
            dict: Dictionary with event details
        """
        event_details = {
            'distance': 0,
            'stroke': 'Unknown',
            'is_relay': False
        }
        
        try:
            # Check if it's a relay
            if 'relay' in event_name.lower():
                event_details['is_relay'] = True
            
            # Extract distance
            distance_match = re.search(r'\d+', event_name)
            if distance_match:
                event_details['distance'] = int(distance_match.group())
            
            # Extract stroke
            if 'freestyle' in event_name.lower() or 'free' in event_name.lower():
                event_details['stroke'] = 'Freestyle'
            elif 'backstroke' in event_name.lower() or 'back' in event_name.lower():
                event_details['stroke'] = 'Backstroke'
            elif 'breaststroke' in event_name.lower() or 'breast' in event_name.lower():
                event_details['stroke'] = 'Breaststroke'
            elif 'butterfly' in event_name.lower() or 'fly' in event_name.lower():
                event_details['stroke'] = 'Butterfly'
            elif 'individual medley' in event_name.lower() or 'im' in event_name.lower():
                event_details['stroke'] = 'Individual Medley'
            elif 'medley relay' in event_name.lower():
                event_details['stroke'] = 'Medley Relay'
            
            return event_details
            
        except Exception as e:
            self.logger.error(f"Error parsing event name: {str(e)}")
            return event_details
    
    def _convert_time_to_seconds(self, time_str):
        """
        Convert a time string to seconds.
        
        Args:
            time_str (str): Time string in format MM:SS.ss or SS.ss
            
        Returns:
            float: Time in seconds
        """
        if not time_str or not isinstance(time_str, str):
            return None
        
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
