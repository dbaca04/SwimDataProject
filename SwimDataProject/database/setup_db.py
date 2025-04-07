"""
Database Setup Script

This script initializes the database and creates basic seed data for testing.
"""
import sys
import os
import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from database.database import init_db, drop_db, db_session
from database.models import (
    Swimmer, Event, Team, SwimTime, Meet, DataSource
)


def setup_database(drop_existing=False):
    """
    Set up the database schema and seed with initial data.
    
    Args:
        drop_existing (bool): Whether to drop existing database
    """
    if drop_existing:
        print("Dropping existing database...")
        drop_db()
    
    print("Creating database schema...")
    init_db()
    
    print("Creating seed data...")
    seed_database()
    
    print("Database setup complete!")


def seed_database():
    """Seed the database with initial data for testing."""
    with db_session() as session:
        # Create data sources
        sources = [
            DataSource(
                name="USA Swimming",
                url="https://data.usaswimming.org",
                description="USA Swimming official data",
                scrape_frequency="daily"
            ),
            DataSource(
                name="NISCA",
                url="https://niscaonline.org",
                description="National Interscholastic Swim Coaches Association",
                scrape_frequency="weekly"
            ),
            DataSource(
                name="SwimCloud",
                url="https://www.swimcloud.com",
                description="Swimming times and rankings platform",
                scrape_frequency="weekly"
            )
        ]
        session.add_all(sources)
        session.commit()
        
        # Create some events
        events = [
            Event(
                name="50 Freestyle",
                distance=50,
                stroke="freestyle",
                course="SCY",
                is_relay=False,
                standard_name="50 Freestyle SCY"
            ),
            Event(
                name="100 Freestyle",
                distance=100,
                stroke="freestyle",
                course="SCY",
                is_relay=False,
                standard_name="100 Freestyle SCY"
            ),
            Event(
                name="200 Freestyle",
                distance=200,
                stroke="freestyle",
                course="SCY",
                is_relay=False,
                standard_name="200 Freestyle SCY"
            ),
            Event(
                name="100 Backstroke",
                distance=100,
                stroke="backstroke",
                course="SCY",
                is_relay=False,
                standard_name="100 Backstroke SCY"
            ),
            Event(
                name="100 Breaststroke",
                distance=100,
                stroke="breaststroke",
                course="SCY",
                is_relay=False,
                standard_name="100 Breaststroke SCY"
            ),
            Event(
                name="100 Butterfly",
                distance=100,
                stroke="butterfly",
                course="SCY",
                is_relay=False,
                standard_name="100 Butterfly SCY"
            ),
            Event(
                name="200 IM",
                distance=200,
                stroke="individual medley",
                course="SCY",
                is_relay=False,
                standard_name="200 Individual Medley SCY"
            ),
            Event(
                name="400 IM",
                distance=400,
                stroke="individual medley",
                course="SCY",
                is_relay=False,
                standard_name="400 Individual Medley SCY"
            ),
            Event(
                name="200 Medley Relay",
                distance=200,
                stroke="medley relay",
                course="SCY",
                is_relay=True,
                standard_name="200 Medley Relay SCY"
            ),
            Event(
                name="200 Freestyle Relay",
                distance=200,
                stroke="freestyle relay",
                course="SCY",
                is_relay=True,
                standard_name="200 Freestyle Relay SCY"
            )
        ]
        session.add_all(events)
        session.commit()
        
        # Create some teams
        teams = [
            Team(
                name="Lincoln High School",
                short_name="Lincoln",
                type="high_school",
                state="CA",
                country="USA"
            ),
            Team(
                name="Washington High School",
                short_name="Washington",
                type="high_school",
                state="CA",
                country="USA"
            ),
            Team(
                name="Palo Alto Swim Club",
                short_name="PASC",
                type="club",
                state="CA",
                country="USA"
            ),
            Team(
                name="Austin Aquatics",
                short_name="AA",
                type="club",
                state="TX",
                country="USA"
            )
        ]
        session.add_all(teams)
        session.commit()
        
        # Create some meets
        meets = [
            Meet(
                name="California State Championships 2024",
                start_date=datetime.date(2024, 5, 15),
                end_date=datetime.date(2024, 5, 17),
                location="Los Angeles, CA",
                course="SCY",
                meet_type="high_school",
                is_observed=True,
                source="USA Swimming",
                source_id="CA2024STATE"
            ),
            Meet(
                name="Lincoln vs Washington Dual Meet",
                start_date=datetime.date(2024, 4, 10),
                end_date=datetime.date(2024, 4, 10),
                location="San Francisco, CA",
                course="SCY",
                meet_type="high_school",
                is_observed=False,
                source="Lincoln High School",
                source_id="LW2024DUAL"
            ),
            Meet(
                name="Spring Invitational 2024",
                start_date=datetime.date(2024, 3, 22),
                end_date=datetime.date(2024, 3, 24),
                location="Palo Alto, CA",
                course="SCY",
                meet_type="club",
                is_observed=True,
                source="USA Swimming",
                source_id="SPRING2024INV"
            )
        ]
        session.add_all(meets)
        session.commit()
        
        # Create some swimmers
        swimmers = [
            Swimmer(
                primary_name="John Smith",
                gender="M",
                birth_year=2007,
                current_age=17,
                state="CA",
                country="USA"
            ),
            Swimmer(
                primary_name="Emily Johnson",
                gender="F",
                birth_year=2006,
                current_age=18,
                state="CA",
                country="USA"
            ),
            Swimmer(
                primary_name="Michael Brown",
                gender="M",
                birth_year=2008,
                current_age=16,
                state="TX",
                country="USA"
            ),
            Swimmer(
                primary_name="Sophia Williams",
                gender="F",
                birth_year=2007,
                current_age=17,
                state="CA",
                country="USA"
            )
        ]
        session.add_all(swimmers)
        session.commit()
        
        # Create some swim times
        times = [
            SwimTime(
                swimmer_id=1,
                event_id=1,
                meet_id=1,
                team_id=1,
                time_seconds=22.34,
                time_formatted="22.34",
                date=datetime.date(2024, 5, 15),
                swimmer_age=17,
                source="USA Swimming",
                source_id="CA2024STATE-50FREE-1"
            ),
            SwimTime(
                swimmer_id=1,
                event_id=2,
                meet_id=1,
                team_id=1,
                time_seconds=49.87,
                time_formatted="49.87",
                date=datetime.date(2024, 5, 16),
                swimmer_age=17,
                source="USA Swimming",
                source_id="CA2024STATE-100FREE-1"
            ),
            SwimTime(
                swimmer_id=2,
                event_id=4,
                meet_id=1,
                team_id=2,
                time_seconds=59.23,
                time_formatted="59.23",
                date=datetime.date(2024, 5, 15),
                swimmer_age=18,
                source="USA Swimming",
                source_id="CA2024STATE-100BACK-2"
            ),
            SwimTime(
                swimmer_id=3,
                event_id=2,
                meet_id=3,
                team_id=4,
                time_seconds=48.76,
                time_formatted="48.76",
                date=datetime.date(2024, 3, 23),
                swimmer_age=16,
                source="USA Swimming",
                source_id="SPRING2024INV-100FREE-3"
            ),
            SwimTime(
                swimmer_id=4,
                event_id=6,
                meet_id=3,
                team_id=3,
                time_seconds=57.89,
                time_formatted="57.89",
                date=datetime.date(2024, 3, 24),
                swimmer_age=17,
                source="USA Swimming",
                source_id="SPRING2024INV-100FLY-4"
            )
        ]
        session.add_all(times)
        session.commit()


if __name__ == "__main__":
    # Parse command line args
    import argparse
    parser = argparse.ArgumentParser(description="Set up the database")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing database before creating new one"
    )
    args = parser.parse_args()
    
    # Set up the database
    setup_database(drop_existing=args.drop)
