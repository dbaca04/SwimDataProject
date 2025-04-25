"""
Test script for the USA Swimming scraper.

This script demonstrates the use of the USA Swimming scraper
with various search strategies.
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
from scrapers.usa_swimming_scraper import USASwimmingScraper

def test_swimmer_search():
    """Test searching for a specific swimmer."""
    # Create scraper with headless mode disabled for demonstration
    scraper = USASwimmingScraper(config={'headless': False})
    
    # Search for a well-known swimmer
    results = scraper.scrape_by_swimmer_name('Katie', 'Ledecky')
    
    print(f"Found {len(results)} results for Katie Ledecky")
    
    # Print first few results
    for i, result in enumerate(results[:5]):
        print(f"\nResult {i+1}:")
        print(f"  Event: {result['event']['name']}")
        print(f"  Time: {result['time']['formatted']}")
        print(f"  Meet: {result['meet']['name']} on {result['meet']['date']}")

def test_event_search():
    """Test searching for a specific event."""
    # Create scraper
    scraper = USASwimmingScraper(config={'headless': False})
    
    # Search for an event with age group filter
    results = scraper.scrape_by_event('100 Freestyle', gender='F', age_group=(15, 18))
    
    print(f"Found {len(results)} results for 100 Freestyle (Female, 15-18)")
    
    # Print first few results
    for i, result in enumerate(results[:5]):
        print(f"\nResult {i+1}:")
        print(f"  Swimmer: {result['swimmer']['full_name']}, Age: {result['swimmer']['age']}")
        print(f"  Time: {result['time']['formatted']}")
        print(f"  Meet: {result['meet']['name']}")

def test_state_search():
    """Test searching for swimmers in a specific state."""
    # Create scraper
    scraper = USASwimmingScraper(config={'headless': False})
    
    # Create search parameters for California
    search_params = {
        'state': 'California',
        'start_date': '01/01/2024',  # Adjust date as needed
    }
    
    # Scrape with limited pages for testing
    results = scraper.scrape_individual_times(search_params, max_pages=2)
    
    print(f"Found {len(results)} results for California")
    
    # Print first few results
    for i, result in enumerate(results[:5]):
        print(f"\nResult {i+1}:")
        print(f"  Swimmer: {result['swimmer']['full_name']}, Age: {result['swimmer']['age']}")
        print(f"  Team: {result['swimmer']['team']}")
        print(f"  Event: {result['event']['name']}")
        print(f"  Time: {result['time']['formatted']}")

def test_full_scrape(max_states=2, swimmers_per_state=20):
    """Test the full scraping process with limited scope."""
    # Create scraper
    scraper = USASwimmingScraper(config={'headless': True})
    
    start_time = datetime.now()
    print(f"Starting scrape at {start_time}")
    
    # Run the scrape with limited scope for testing
    results = scraper.scrape(max_states=max_states, swimmers_per_state=swimmers_per_state)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"Scrape completed at {end_time}")
    print(f"Duration: {duration}")
    print(f"Found {len(results)} results")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test USA Swimming scraper')
    parser.add_argument('--test', choices=['swimmer', 'event', 'state', 'full'], 
                        default='swimmer', help='Test type to run')
    
    args = parser.parse_args()
    
    if args.test == 'swimmer':
        test_swimmer_search()
    elif args.test == 'event':
        test_event_search()
    elif args.test == 'state':
        test_state_search()
    elif args.test == 'full':
        test_full_scrape()
