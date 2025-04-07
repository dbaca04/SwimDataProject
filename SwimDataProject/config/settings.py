"""
Application settings for the Swim Data Project.
"""

import os
from typing import Dict, Any

# Database settings
DATABASE = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'swim_data'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'min_connections': int(os.environ.get('DB_MIN_CONN', 1)),
    'max_connections': int(os.environ.get('DB_MAX_CONN', 10)),
}

# Scraper settings
SCRAPER = {
    'usa_swimming': {
        'base_url': 'https://data.usaswimming.org',
        'min_delay': 2,  # Minimum delay between requests in seconds
        'max_delay': 5,  # Maximum delay between requests in seconds
        'max_pages': 10,  # Maximum number of pages to scrape per query
        'headless': True,  # Whether to run browser in headless mode
        'times_search_params': {
            # Default search parameters for times
            'start_date': '2023-01-01',
            'end_date': '',  # Empty for current date
        },
        'rankings_search_params': {
            # Default search parameters for rankings
            'season': '2023-2024',
            'geography': 'national'
        }
    },
    'nisca': {
        'base_url': 'https://niscaonline.org',
        'min_delay': 3,
        'max_delay': 6,
        'headless': True
    },
    'swimcloud': {
        'base_url': 'https://www.swimcloud.com',
        'min_delay': 2,
        'max_delay': 5,
        'headless': True
    },
    'state_associations': {
        # Configuration for state athletic associations
        'states': ['CA', 'TX', 'FL', 'IL', 'OH', 'PA'],  # Priority states
        'min_delay': 3,
        'max_delay': 7,
        'headless': True
    }
}

# Proxy settings
PROXY = {
    'use_proxy': bool(os.environ.get('USE_PROXY', False)),
    'proxy_list_url': os.environ.get('PROXY_LIST_URL', ''),
    'proxy_list_file': os.environ.get('PROXY_LIST_FILE', ''),
    'proxy_username': os.environ.get('PROXY_USERNAME', ''),
    'proxy_password': os.environ.get('PROXY_PASSWORD', '')
}

# API settings
API = {
    'host': os.environ.get('API_HOST', '0.0.0.0'),
    'port': int(os.environ.get('API_PORT', 8000)),
    'debug': bool(os.environ.get('API_DEBUG', True)),
    'log_level': os.environ.get('API_LOG_LEVEL', 'info'),
    'cors_origins': os.environ.get('CORS_ORIGINS', '*').split(','),
    'rate_limit': int(os.environ.get('RATE_LIMIT', 100)),  # Requests per minute
}

# Logging settings
LOGGING = {
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.environ.get('LOG_FILE', ''),
    'rotation': int(os.environ.get('LOG_ROTATION', 1024 * 1024 * 10)),  # 10 MB
    'backups': int(os.environ.get('LOG_BACKUPS', 5))
}

# Common application settings
APP = {
    'name': 'SwimDataProject',
    'version': '0.1.0',
    'description': 'Swimming data platform for high school swimmers',
    'environment': os.environ.get('ENVIRONMENT', 'development'),
    'data_dir': os.environ.get('DATA_DIR', 'data'),
    'temp_dir': os.environ.get('TEMP_DIR', 'temp')
}

def get_config():
    """Get the full application configuration"""
    return {
        'DATABASE': DATABASE,
        'SCRAPER': SCRAPER,
        'PROXY': PROXY,
        'API': API,
        'LOGGING': LOGGING,
        'APP': APP
    }
