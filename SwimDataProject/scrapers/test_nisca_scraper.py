"""
Test script for the NISCA scraper.

This script demonstrates the use of the NISCA scraper
to collect high school swimming records and All-America lists.
"""
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path to allow importing from database
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the scraper
from scrapers.nisca_scraper import NIScAScraper

def test_records_scraping():
    """Test scraping of national high school records."""
    # Create scraper with headless mode disabled for demonstration
    scraper = NIScAScraper(config={'headless': False})
    
    # Scrape male records
    male_records = scraper.scrape_records(gender='male')
    
    print(f"Found {len(male_records)} male records")
    
    # Print some sample records
    for i, (key, record) in enumerate(male_records.items()):
        if i < 5:  # Just print the first 5 records
            print(f"\nRecord: {record['event']}")
            print(f"  Time: {record['time']}")
            print(f"  Name: {record['name']}")
            print(f"  School: {record['school']}")
            print(f"  Year: {record['year']}")
        else:
            break
    
    # Scrape female records
    female_records = scraper.scrape_records(gender='female')
    
    print(f"\nFound {len(female_records)} female records")
    
    # Print some sample records
    for i, (key, record) in enumerate(female_records.items()):
        if i < 5:  # Just print the first 5 records
            print(f"\nRecord: {record['event']}")
            print(f"  Time: {record['time']}")
            print(f"  Name: {record['name']}")
            print(f"  School: {record['school']}")
            print(f"  Year: {record['year']}")
        else:
            break

def test_all_america_scraping():
    """Test scraping of All-America lists."""
    # Create scraper with headless mode disabled for demonstration
    scraper = NIScAScraper(config={'headless': False})
    
    # Scrape All-America lists
    all_america = scraper.scrape_all_america()
    
    print(f"Found All-America lists for {len(all_america)} years")
    
    # Print some sample data
    for year, categories in all_america.items():
        print(f"\nYear: {year}")
        for category, data in categories.items():
            if isinstance(data, dict):  # If this is a processed list with events
                print(f"  Category: {category}")
                print(f"  Events: {len(data)}")
                
                # Print first event details
                if data:
                    first_event = next(iter(data))
                    swimmers = data[first_event]
                    print(f"  Sample event: {first_event}")
                    print(f"  Swimmers in event: {len(swimmers)}")
                    
                    # Print first few swimmers
                    for i, swimmer in enumerate(swimmers):
                        if i < 3:  # Just print the first 3 swimmers
                            print(f"    Swimmer {i+1}: {swimmer['name']}")
                            print(f"      School: {swimmer['school']}")
                            print(f"      Time: {swimmer['time']}")
                        else:
                            break
            else:
                print(f"  Category: {category} (URL only)")

def test_full_scrape():
    """Test the full scraping process."""
    # Create scraper
    scraper = NIScAScraper(config={'headless': True})
    
    start_time = datetime.now()
    print(f"Starting scrape at {start_time}")
    
    # Run the scrape
    data = scraper.scrape()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"Scrape completed at {end_time}")
    print(f"Duration: {duration}")
    
    # Print summary
    male_records = data['records'].get('male', {})
    female_records = data['records'].get('female', {})
    all_america = data['all_america']
    
    print(f"Found {len(male_records)} male records")
    print(f"Found {len(female_records)} female records")
    print(f"Found All-America lists for {len(all_america)} years")
    
    # Save data
    records_saved = scraper.save_data(data)
    print(f"Saved {records_saved} records to database")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test NISCA scraper')
    parser.add_argument('--test', choices=['records', 'all_america', 'full'], 
                        default='records', help='Test type to run')
    
    args = parser.parse_args()
    
    if args.test == 'records':
        test_records_scraping()
    elif args.test == 'all_america':
        test_all_america_scraping()
    elif args.test == 'full':
        test_full_scrape()
