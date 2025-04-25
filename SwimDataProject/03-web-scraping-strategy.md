# Web Scraping Strategy

This document outlines our approach to collecting swimming data through web scraping. The strategy focuses on ethical data collection, technical implementation, and ensuring data quality.

## Priority Targets

We'll prioritize our scraping efforts based on data value, accessibility, and update frequency:

### Tier 1 (Primary Sources)

1. **USA Swimming Data Hub**
   - Target URLs:
     - Individual Times Search: https://data.usaswimming.org/datahub/usas/individualsearch
     - Event Rankings: https://data.usaswimming.org/datahub/usas/timeseventrank
     - Top Times Search: https://www.usaswimming.org/times/data-hub/top-times-search
     - Age Group Records: https://www.usaswimming.org/times/popular-resources/national-age-group-records
   - Update frequency: Daily
   - Priority data: Individual times, rankings, meet results

2. **NISCA Records and Rankings**
   - Target URLs:
     - Records: https://niscaonline.org/index.php/records
     - All-America: https://niscaonline.org/index.php/all-america/swimming
   - Update frequency: Aligned with publication (typically annual)
   - Priority data: National high school records, All-American lists

3. **Top State Athletic Associations** (starting with largest swimming programs)
   - Initial targets: California, Texas, Florida, Illinois, Ohio, Pennsylvania
   - Update frequency: Aligned with competition seasons
   - Priority data: State championship results, qualifying times, state records

### Tier 2 (Supplementary Sources)

1. **SwimCloud**
   - Target sections:
     - Rankings: https://www.swimcloud.com/rankings/
     - Results: https://www.swimcloud.com/results/
   - Update frequency: Weekly
   - Priority data: Additional rankings, team data, college recruiting benchmarks

2. **SwimStandards**
   - Target URL: https://swimstandards.com
   - Update frequency: Monthly
   - Priority data: Time standards, additional swimmer profiles

3. **SwimRankings.net**
   - Target URL: https://www.swimrankings.net/
   - Update frequency: Monthly
   - Priority data: International comparison data, global rankings

## Technical Implementation

### 1. Scraping Infrastructure

```python
# Core scraper class structure
class SwimScraper:
    def __init__(self, source_name, base_url, config):
        self.source_name = source_name
        self.base_url = base_url
        self.config = config
        self.session = self._init_session()
        self.db_connection = self._init_database()
        self.logger = self._init_logger()
        
    def _init_session(self):
        """Initialize session with appropriate headers and proxies if needed"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        if self.config.get('use_proxy', False):
            session.proxies = self._get_proxy()
        
        return session
    
    def scrape(self):
        """Main scraping method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape()")
    
    def save_data(self, data):
        """Save scraped data to database"""
        raise NotImplementedError("Subclasses must implement save_data()")
    
    def _get_random_user_agent(self):
        """Return a random user agent from the pool"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            # Add more user agents
        ]
        return random.choice(user_agents)
    
    def _get_proxy(self):
        """Return a proxy from the pool"""
        # Implementation will depend on proxy provider
        pass
```

### 2. Source-Specific Implementations

#### USA Swimming Scraper

```python
class USASwimmingScraper(SwimScraper):
    def __init__(self, config):
        super().__init__('usa_swimming', 'https://data.usaswimming.org', config)
        self.driver = self._init_selenium_driver()
    
    def _init_selenium_driver(self):
        """Initialize a Selenium driver with anti-detection measures"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self._get_random_user_agent()}')
        
        # Disable automation flags
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        # Execute CDP commands to disable webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
    
    def scrape_individual_times(self, search_params):
        """Scrape individual times using search parameters"""
        try:
            # Navigate to search page
            self.driver.get(f"{self.base_url}/datahub/usas/individualsearch")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "swimmer-search-form"))
            )
            
            # Fill in search form
            self._fill_search_form(search_params)
            
            # Extract results
            results = self._extract_results()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error scraping individual times: {str(e)}")
            return []
    
    def _fill_search_form(self, search_params):
        """Fill in the search form with provided parameters"""
        # Implementation details specific to USA Swimming search form
        pass
    
    def _extract_results(self):
        """Extract results from the page after search"""
        # Implementation details specific to USA Swimming results page
        pass
```

#### NISCA Scraper

```python
class NIScAScraper(SwimScraper):
    def __init__(self, config):
        super().__init__('nisca', 'https://niscaonline.org', config)
    
    def scrape_records(self):
        """Scrape national high school records"""
        try:
            response = self.session.get(f"{self.base_url}/index.php/records")
            
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch records page: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract records tables
            records = []
            record_tables = soup.select('.record-table')
            
            for table in record_tables:
                records.extend(self._parse_record_table(table))
            
            return records
            
        except Exception as e:
            self.logger.error(f"Error scraping NISCA records: {str(e)}")
            return []
    
    def _parse_record_table(self, table):
        """Parse a record table to extract structured data"""
        # Implementation details specific to NISCA record tables
        pass
```

### 3. Rate Limiting and Ethical Scraping

```python
class RateLimiter:
    """Rate limiter to ensure ethical scraping"""
    
    def __init__(self, requests_per_minute=10, requests_per_hour=100):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = []
        self.hour_requests = []
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        now = time.time()
        
        # Clean up old timestamps
        self.minute_requests = [t for t in self.minute_requests if now - t < 60]
        self.hour_requests = [t for t in self.hour_requests if now - t < 3600]
        
        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.minute_requests[0]) + random.uniform(0.1, 1.0)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Check hour limit
        if len(self.hour_requests) >= self.requests_per_hour:
            sleep_time = 3600 - (now - self.hour_requests[0]) + random.uniform(1.0, 5.0)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Add current request
        now = time.time()  # Update time after potential waiting
        self.minute_requests.append(now)
        self.hour_requests.append(now)
```

### 4. Proxy Rotation and IP Management

```python
class ProxyManager:
    """Manage a pool of proxies for scraping"""
    
    def __init__(self, proxy_list_url=None, proxy_list_file=None):
        self.proxies = []
        self.proxy_performance = {}
        
        if proxy_list_url:
            self.load_proxies_from_url(proxy_list_url)
        elif proxy_list_file:
            self.load_proxies_from_file(proxy_list_file)
    
    def load_proxies_from_url(self, url):
        """Load proxies from a proxy provider URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                self.logger.info(f"Loaded {len(self.proxies)} proxies from URL")
        except Exception as e:
            self.logger.error(f"Error loading proxies from URL: {str(e)}")
    
    def load_proxies_from_file(self, file_path):
        """Load proxies from a local file"""
        try:
            with open(file_path, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
                self.logger.info(f"Loaded {len(self.proxies)} proxies from file")
        except Exception as e:
            self.logger.error(f"Error loading proxies from file: {str(e)}")
    
    def get_proxy(self):
        """Get a proxy from the pool, preferring better performing ones"""
        if not self.proxies:
            return None
        
        # Prefer proxies with better performance
        working_proxies = [p for p in self.proxies if self.proxy_performance.get(p, 0) >= 0]
        
        if working_proxies:
            return random.choice(working_proxies)
        else:
            return random.choice(self.proxies)
    
    def report_proxy_success(self, proxy):
        """Report successful use of a proxy"""
        current_score = self.proxy_performance.get(proxy, 0)
        self.proxy_performance[proxy] = min(current_score + 1, 10)
    
    def report_proxy_failure(self, proxy):
        """Report failure of a proxy"""
        current_score = self.proxy_performance.get(proxy, 0)
        self.proxy_performance[proxy] = max(current_score - 2, -5)
        
        # Remove proxy if it consistently fails
        if self.proxy_performance[proxy] <= -5:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                self.logger.info(f"Removed consistently failing proxy: {proxy}")
```

## Data Extraction and Parsing

### 1. Swimmer Data Model

```python
class SwimmerData:
    """Model for storing swimmer data"""
    
    def __init__(self, source, source_id=None):
        self.source = source
        self.source_id = source_id
        self.names = []  # To handle name variations
        self.primary_name = None
        self.gender = None
        self.birth_year = None
        self.teams = []  # To handle multiple teams (high school, club)
        self.schools = []  # To handle school changes
        self.state = None
        self.times = []  # Swim times
        self.rankings = []  # Rankings data
        self.last_updated = datetime.datetime.now()
    
    def add_name(self, name, is_primary=False):
        """Add a name variation for the swimmer"""
        if name not in self.names:
            self.names.append(name)
        
        if is_primary or self.primary_name is None:
            self.primary_name = name
    
    def add_team(self, team_name, team_type, start_date=None, end_date=None):
        """Add a team affiliation"""
        self.teams.append({
            'name': team_name,
            'type': team_type,  # 'high_school', 'club', etc.
            'start_date': start_date,
            'end_date': end_date
        })
    
    def add_school(self, school_name, start_date=None, end_date=None):
        """Add a school affiliation"""
        self.schools.append({
            'name': school_name,
            'start_date': start_date,
            'end_date': end_date
        })
    
    def add_time(self, event, time_value, meet_name, meet_date, source):
        """Add a swim time"""
        self.times.append({
            'event': event,
            'time': time_value,
            'meet_name': meet_name,
            'meet_date': meet_date,
            'source': source,
            'added_date': datetime.datetime.now()
        })
    
    def add_ranking(self, event, rank, scope, ranking_date, source):
        """Add a ranking"""
        self.rankings.append({
            'event': event,
            'rank': rank,
            'scope': scope,  # 'national', 'state', etc.
            'date': ranking_date,
            'source': source,
            'added_date': datetime.datetime.now()
        })
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'source': self.source,
            'source_id': self.source_id,
            'names': self.names,
            'primary_name': self.primary_name,
            'gender': self.gender,
            'birth_year': self.birth_year,
            'teams': self.teams,
            'schools': self.schools,
            'state': self.state,
            'times': self.times,
            'rankings': self.rankings,
            'last_updated': self.last_updated
        }
```

### 2. Event Standardization

```python
class EventStandardizer:
    """Standardize event names across different sources"""
    
    def __init__(self):
        self.event_mapping = {
            # Standard formats
            '50 Free': '50 Freestyle',
            '100 Free': '100 Freestyle',
            '200 Free': '200 Freestyle',
            '500 Free': '500 Freestyle',
            '1000 Free': '1000 Freestyle',
            '1650 Free': '1650 Freestyle',
            # Add more mappings
        }
        
        # Regular expressions for complex matching
        self.regex_patterns = [
            (re.compile(r'50\s*(?:yard|yd|y)?\s*(?:freestyle|free)', re.I), '50 Freestyle'),
            (re.compile(r'100\s*(?:yard|yd|y)?\s*(?:freestyle|free)', re.I), '100 Freestyle'),
            # Add more patterns
        ]
    
    def standardize(self, event_name):
        """Convert event name to standard format"""
        # Check direct mapping
        if event_name in self.event_mapping:
            return self.event_mapping[event_name]
        
        # Check regex patterns
        for pattern, standard_name in self.regex_patterns:
            if pattern.match(event_name):
                return standard_name
        
        # If no match, return original with warning
        logging.warning(f"No standardization for event: {event_name}")
        return event_name
```

### 3. Time Parsing

```python
class TimeParser:
    """Parse and convert swimming times"""
    
    @staticmethod
    def parse_time(time_str):
        """Convert time string to seconds"""
        time_str = time_str.strip()
        
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
    
    @staticmethod
    def format_time(seconds, include_hundredths=True):
        """Convert seconds to formatted time string"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        
        if include_hundredths:
            return f"{minutes}:{remaining_seconds:06.2f}" if minutes > 0 else f"{remaining_seconds:.2f}"
        else:
            return f"{minutes}:{int(remaining_seconds):02d}" if minutes > 0 else f"{int(remaining_seconds)}"
    
    @staticmethod
    def convert_course(time_seconds, from_course, to_course):
        """Convert times between different course types (SCY, SCM, LCM)"""
        # Simplified conversion factors
        # In reality, these would be event-specific
        conversion_factors = {
            ('SCY', 'SCM'): 1.11,  # SCY to SCM
            ('SCY', 'LCM'): 1.13,  # SCY to LCM
            ('SCM', 'SCY'): 0.9,   # SCM to SCY
            ('SCM', 'LCM'): 1.02,  # SCM to LCM
            ('LCM', 'SCY'): 0.885, # LCM to SCY
            ('LCM', 'SCM'): 0.98   # LCM to SCM
        }
        
        # Same course, no conversion needed
        if from_course == to_course:
            return time_seconds
        
        # Apply conversion factor
        factor = conversion_factors.get((from_course, to_course))
        if factor:
            return time_seconds * factor
        else:
            raise ValueError(f"No conversion factor for {from_course} to {to_course}")
```

## Error Handling and Resilience

### 1. Retry Mechanism

```python
def retry_on_failure(max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """Decorator for retrying functions that may fail temporarily"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    # Calculate backoff time
                    backoff_time = backoff_factor ** attempt
                    # Add some randomness
                    backoff_time += random.uniform(0, 0.5 * backoff_time)
                    # Log retry
                    logging.warning(f"Retry {attempt+1}/{max_retries} after error: {str(e)}. Waiting {backoff_time:.2f}s")
                    # Wait before retrying
                    time.sleep(backoff_time)
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        return wrapper
    return decorator
```

### 2. Incremental Processing

```python
class IncrementalScraper:
    """Base class for scrapers that support incremental updates"""
    
    def __init__(self, source_name, base_url, config, storage):
        self.source_name = source_name
        self.base_url = base_url
        self.config = config
        self.storage = storage
    
    def get_last_run_timestamp(self):
        """Get timestamp of last successful run"""
        return self.storage.get_last_run(self.source_name)
    
    def save_run_timestamp(self):
        """Save timestamp of current run"""
        self.storage.save_last_run(self.source_name, datetime.datetime.now())
    
    def get_new_data_since(self, timestamp):
        """Get data updated since the given timestamp"""
        raise NotImplementedError("Subclasses must implement get_new_data_since()")
    
    def run_incremental_update(self):
        """Run an incremental update"""
        try:
            last_run = self.get_last_run_timestamp()
            
            if last_run:
                # Get data updated since last run
                new_data = self.get_new_data_since(last_run)
                logging.info(f"Found {len(new_data)} updated items since {last_run}")
            else:
                # First run, get all data
                new_data = self.get_all_data()
                logging.info(f"First run, found {len(new_data)} items")
            
            # Save data
            if new_data:
                self.save_data(new_data)
            
            # Update timestamp
            self.save_run_timestamp()
            
            return len(new_data)
            
        except Exception as e:
            logging.error(f"Error in incremental update: {str(e)}")
            return 0
```

### 3. Monitoring and Alerting

```python
class ScraperMonitor:
    """Monitor scraper health and send alerts on issues"""
    
    def __init__(self, config, alert_channels=None):
        self.config = config
        self.alert_channels = alert_channels or []
        self.stats = {}
    
    def record_scrape_start(self, source_name):
        """Record the start of a scrape operation"""
        self.stats[source_name] = {
            'start_time': datetime.datetime.now(),
            'status': 'running',
            'records_processed': 0,
            'errors': []
        }
    
    def record_scrape_error(self, source_name, error):
        """Record an error during scraping"""
        if source_name in self.stats:
            self.stats[source_name]['errors'].append({
                'time': datetime.datetime.now(),
                'message': str(error)
            })
            
            # Check if error count exceeds threshold
            if len(self.stats[source_name]['errors']) >= self.config.get('error_threshold', 5):
                self.send_alert(f"Error threshold exceeded for {source_name}", 
                                f"{len(self.stats[source_name]['errors'])} errors occurred")
    
    def record_scrape_progress(self, source_name, records_processed):
        """Record progress of scraping"""
        if source_name in self.stats:
            self.stats[source_name]['records_processed'] = records_processed
    
    def record_scrape_complete(self, source_name, success=True):
        """Record completion of scraping"""
        if source_name in self.stats:
            end_time = datetime.datetime.now()
            self.stats[source_name]['end_time'] = end_time
            self.stats[source_name]['duration'] = (end_time - self.stats[source_name]['start_time']).total_seconds()
            self.stats[source_name]['status'] = 'success' if success else 'failed'
            
            # Check if duration exceeds threshold
            if self.stats[source_name]['duration'] > self.config.get('duration_threshold', 3600):
                self.send_alert(f"Long running scrape for {source_name}", 
                                f"Scrape took {self.stats[source_name]['duration']} seconds")
    
    def send_alert(self, subject, message):
        """Send alert through configured channels"""
        for channel in self.alert_channels:
            try:
                channel.send(subject, message)
            except Exception as e:
                logging.error(f"Failed to send alert through {channel.__class__.__name__}: {str(e)}")
    
    def get_stats(self, source_name=None):
        """Get stats for a source or all sources"""
        if source_name:
            return self.stats.get(source_name)
        else:
            return self.stats
```

## Ethical Considerations

### 1. Compliance with Terms of Service

- We will respect the `robots.txt` file of each website and adhere to its directives.
- When available, we will use official APIs rather than scraping.
- We will identify our scraper in user-agent strings as appropriate.
- We will not attempt to circumvent explicit anti-scraping measures.

### 2. Server Load Considerations

- Rate limiting will be implemented for all scrapers to minimize impact.
- Scraping will be scheduled during off-peak hours when possible.
- Incremental scraping will be used to reduce unnecessary data transfer.
- Caching will be implemented to avoid redundant requests.

### 3. Data Privacy Practices

- Personal information beyond what is publicly available will not be collected.
- Data will be stored securely with appropriate access controls.
- All data will include source attribution.
- We will provide a mechanism for data removal upon request.

## Implementation Schedule

| Phase | Focus | Timeline | Success Criteria |
|-------|-------|----------|------------------|
| 1 | Proof of Concept | Weeks 1-2 | Successful scraping of one primary source |
| 2 | Core Infrastructure | Weeks 3-5 | Framework for all scrapers, database schema |
| 3 | Primary Sources | Weeks 6-8 | All Tier 1 sources operational |
| 4 | Secondary Sources | Weeks 9-10 | All Tier 2 sources operational |
| 5 | Integration and Testing | Weeks 11-12 | Data quality verification, performance optimization |

## Maintenance Plan

- Regular code reviews and updates to maintain compatibility with source websites
- Weekly verification of scraper health and data quality
- Monthly assessment of new data sources to potentially incorporate
- Quarterly review of ethical practices and compliance with terms of service
- Documentation updates as the system evolves
