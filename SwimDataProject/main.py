#!/usr/bin/env python3
"""
Main entry point for the Swim Data Project.
"""

import argparse
import logging
import sys
from typing import List

from config.settings import get_config
from database.database import Database
from scrapers.usa_swimming_scraper import USASwimmingScraper
from scrapers.nisca_scraper import NIScAScraper
from api.app import start as start_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

def run_scraper(scraper_name: str, config: dict, **kwargs) -> bool:
    """
    Run a specific scraper.
    
    Args:
        scraper_name: Name of the scraper to run
        config: Configuration object
        **kwargs: Additional arguments to pass to the scraper
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running scraper: {scraper_name}")
    
    scraper_config = config.get('SCRAPER', {}).get(scraper_name, {})
    
    # Apply any overrides from kwargs
    if kwargs:
        scraper_config.update(kwargs)
    
    if scraper_name == "usa_swimming":
        # Get additional parameters from command line
        max_states = kwargs.get('max_states', 5)
        swimmers_per_state = kwargs.get('swimmers_per_state', 100)
        headless = kwargs.get('headless', True)
        
        # Create the scraper with configured settings
        scraper_config = scraper_config or {}
        scraper_config['headless'] = headless
        
        scraper = USASwimmingScraper(scraper_config)
        
        # Execute the scrape
        try:
            data = scraper.scrape(max_states=max_states, swimmers_per_state=swimmers_per_state)
            records_saved = len(data)
            logger.info(f"Scraper completed successfully, found {records_saved} records")
            return True
        except Exception as e:
            logger.error(f"Error running USA Swimming scraper: {str(e)}")
            return False
            
    elif scraper_name == "nisca":
        # Get additional parameters from command line
        headless = kwargs.get('headless', True)
        
        # Create the scraper with configured settings
        scraper_config = scraper_config or {}
        scraper_config['headless'] = headless
        
        scraper = NIScAScraper(scraper_config)
        
        # Execute the scrape
        try:
            data = scraper.scrape()
            records_saved = scraper.save_data(data)
            
            male_records = data['records'].get('male', {})
            female_records = data['records'].get('female', {})
            all_america = data['all_america']
            
            logger.info(f"Found {len(male_records)} male records")
            logger.info(f"Found {len(female_records)} female records")
            logger.info(f"Found All-America lists for {len(all_america)} years")
            logger.info(f"Saved {records_saved} records to database")
            
            return True
        except Exception as e:
            logger.error(f"Error running NISCA scraper: {str(e)}")
            return False
    elif scraper_name == "swimcloud":
        logger.error("SwimCloud scraper not yet implemented")
        return False
    elif scraper_name == "state":
        logger.error("State association scrapers not yet implemented")
        return False
    else:
        logger.error(f"Unknown scraper: {scraper_name}")
        return False

def run_api() -> None:
    """Run the API server"""
    logger.info("Starting API server")
    start_api()

def init_db() -> bool:
    """
    Initialize the database.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing database")
    
    try:
        from database.init_db import create_database, execute_schema
        import os
        
        config = get_config()
        db_config = config['DATABASE']
        
        # Create database
        if not create_database(db_config):
            return False
        
        # Execute schema
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, 'database', 'schema.sql')
        
        if not execute_schema(db_config, schema_path):
            return False
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

def main(args: List[str] = None) -> int:
    """
    Main entry point.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="Swim Data Project")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Init DB command
    init_parser = subparsers.add_parser('init-db', help='Initialize the database')
    
    # Scraper command
    scraper_parser = subparsers.add_parser('scrape', help='Run a scraper')
    scraper_parser.add_argument('--name', required=True,
                              choices=['usa_swimming', 'nisca', 'swimcloud', 'state'],
                              help='Name of the scraper to run')
    scraper_parser.add_argument('--max-states', type=int, default=5,
                              help='Maximum number of states to scrape (for USA Swimming)')
    scraper_parser.add_argument('--swimmers-per-state', type=int, default=100,
                              help='Target number of swimmers per state (for USA Swimming)')
    scraper_parser.add_argument('--headless', type=bool, default=True,
                              help='Run in headless mode (no browser UI)')
    scraper_parser.add_argument('--swimmer', type=str,
                              help='Search for a specific swimmer (format: "FirstName LastName")')
    scraper_parser.add_argument('--event', type=str,
                              help='Search for a specific event (e.g., "100 Freestyle")')
    scraper_parser.add_argument('--gender', type=str, choices=['M', 'F'],
                              help='Filter by gender (M or F)')
    scraper_parser.add_argument('--min-age', type=int,
                              help='Minimum age for filtering')
    scraper_parser.add_argument('--max-age', type=int,
                              help='Maximum age for filtering')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Run the API server')
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Get configuration
    config = get_config()
    
    # Execute command
    if parsed_args.command == 'init-db':
        success = init_db()
        return 0 if success else 1
    elif parsed_args.command == 'scrape':
        # Extract scraper parameters from args
        scraper_kwargs = {
            'max_states': parsed_args.max_states,
            'swimmers_per_state': parsed_args.swimmers_per_state,
            'headless': parsed_args.headless
        }
        
        # Handle specific search types
        if parsed_args.swimmer and parsed_args.name == 'usa_swimming':
            # Special case for swimmer search
            try:
                first_name, last_name = parsed_args.swimmer.split(' ', 1)
                # Create the scraper directly
                scraper = USASwimmingScraper({'headless': parsed_args.headless})
                data = scraper.scrape_by_swimmer_name(first_name, last_name)
                logger.info(f"Found {len(data)} results for swimmer {parsed_args.swimmer}")
                success = len(data) > 0
            except Exception as e:
                logger.error(f"Error searching for swimmer: {str(e)}")
                success = False
        elif parsed_args.event and parsed_args.name == 'usa_swimming':
            # Special case for event search
            try:
                # Create age group tuple if both min and max are provided
                age_group = None
                if parsed_args.min_age is not None and parsed_args.max_age is not None:
                    age_group = (parsed_args.min_age, parsed_args.max_age)
                
                # Create the scraper directly
                scraper = USASwimmingScraper({'headless': parsed_args.headless})
                data = scraper.scrape_by_event(parsed_args.event, gender=parsed_args.gender, age_group=age_group)
                logger.info(f"Found {len(data)} results for event {parsed_args.event}")
                success = len(data) > 0
            except Exception as e:
                logger.error(f"Error searching for event: {str(e)}")
                success = False
        else:
            # Normal scraper execution
            success = run_scraper(parsed_args.name, config, **scraper_kwargs)
        
        return 0 if success else 1
    elif parsed_args.command == 'api':
        run_api()
        return 0
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
