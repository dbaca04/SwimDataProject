"""
Initialize the database with schema and initial data.
"""

import os
import logging
import argparse
from typing import Dict, Any

import psycopg2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_init")

def create_database(config: Dict[str, Any]) -> bool:
    """
    Create the database if it doesn't exist.
    
    Args:
        config: Database configuration
        
    Returns:
        True if successful, False otherwise
    """
    # Connect to default database to check if our database exists
    conn = None
    try:
        # Connect to the 'postgres' database to create a new database
        conn = psycopg2.connect(
            host=config.get('host', 'localhost'),
            database='postgres',
            user=config.get('user', 'postgres'),
            password=config.get('password', ''),
            port=config.get('port', 5432)
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        db_name = config.get('database', 'swim_data')
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()

def execute_schema(config: Dict[str, Any], schema_path: str) -> bool:
    """
    Execute the schema SQL file to create tables.
    
    Args:
        config: Database configuration
        schema_path: Path to schema SQL file
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=config.get('host', 'localhost'),
            database=config.get('database', 'swim_data'),
            user=config.get('user', 'postgres'),
            password=config.get('password', ''),
            port=config.get('port', 5432)
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Read and execute schema file
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        
        logger.info(f"Schema executed successfully from {schema_path}")
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error executing schema: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """Main entry point for database initialization"""
    parser = argparse.ArgumentParser(description='Initialize the swim data database')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5432, help='Database port')
    parser.add_argument('--user', default='postgres', help='Database user')
    parser.add_argument('--password', default='', help='Database password')
    parser.add_argument('--database', default='swim_data', help='Database name')
    parser.add_argument('--schema', default='schema.sql', help='Path to schema SQL file')
    
    args = parser.parse_args()
    
    # Build config from arguments
    config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': args.database,
    }
    
    # Create database
    if create_database(config):
        # Get absolute path to schema file
        schema_path = args.schema
        if not os.path.isabs(schema_path):
            # If relative path, assume it's relative to the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(script_dir, schema_path)
        
        # Execute schema
        if execute_schema(config, schema_path):
            logger.info("Database initialization completed successfully")
        else:
            logger.error("Failed to execute schema")
    else:
        logger.error("Failed to create database")

if __name__ == "__main__":
    main()
