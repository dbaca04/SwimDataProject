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
from api.app import start as start_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

def run_scraper(scraper_name: str, config: dict) -> bool:
    """
    Run a specific scraper.
    
    Args:
        scraper_name: Name of the scraper to run
        config: Configuration object
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running scraper: {scraper_name}")
    
    if scraper_name == "usa_swimming":
        scraper = USASwimmingScraper(config['SCRAPER']['usa_swimming'])
        data = scraper.scrape()
        return scraper.save_data(data)
    elif scraper_name == "nisca":
        logger.error("NISCA scraper not yet implemented")
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
        success = run_scraper(parsed_args.name, config)
        return 0 if success else 1
    elif parsed_args.command == 'api':
        run_api()
        return 0
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
