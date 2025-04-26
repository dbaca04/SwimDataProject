#!/usr/bin/env python3
"""
Demo script for swimming analytics.

This script demonstrates the use of swimming analytics and visualization functions
with sample data.
"""
import os
import sys
import logging
import argparse
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("demo")

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import required modules
from database.database import SessionLocal
from database.models import Swimmer, Team, Event, SwimTime, Ranking, TimeStandard, Record

from analysis.swimmer_analysis import (
    calculate_progression,
    compare_with_standards,
    compare_with_elite,
    get_peer_statistics,
    calculate_rankings
)

from analysis.visualization import (
    create_progression_chart,
    create_standards_comparison_chart,
    create_percentile_chart,
    create_peer_distribution_chart,
    create_elite_comparison_chart
)


def create_sample_data(db_session):
    """
    Create sample data for testing analytics.
    
    Args:
        db_session: Database session
        
    Returns:
        dict: Sample data IDs
    """
    logger.info("Creating sample data...")
    
    # Create sample events
    events = []
    
    event_data = [
        {"name": "50 Freestyle", "distance": 50, "stroke": "Freestyle", "course": "SCY", "is_relay": False},
        {"name": "100 Freestyle", "distance": 100, "stroke": "Freestyle", "course": "SCY", "is_relay": False},
        {"name": "200 Freestyle", "distance": 200, "stroke": "Freestyle", "course": "SCY", "is_relay": False},
        {"name": "100 Butterfly", "distance": 100, "stroke": "Butterfly", "course": "SCY", "is_relay": False},
        {"name": "200 Individual Medley", "distance": 200, "stroke": "Individual Medley", "course": "SCY", "is_relay": False}
    ]
    
    for data in event_data:
        event = Event(
            name=data["name"],
            distance=data["distance"],
            stroke=data["stroke"],
            course=data["course"],
            is_relay=data["is_relay"],
            standard_name=data["name"]
        )
        db_session.add(event)
    
    db_session.commit()
    
    # Get the created events
    events = db_session.query(Event).all()
    
    # Create sample swimmers
    swimmers = []
    
    swimmer_data = [
        {"name": "John Smith", "gender": "M", "birth_year": 2007, "current_age": 17, "state": "CA"},
        {"name": "Jane Doe", "gender": "F", "birth_year": 2008, "current_age": 16, "state": "TX"},
        {"name": "Alex Johnson", "gender": "M", "birth_year": 2009, "current_age": 15, "state": "FL"}
    ]
    
    for data in swimmer_data:
        swimmer = Swimmer(
            primary_name=data["name"],
            gender=data["gender"],
            birth_year=data["birth_year"],
            current_age=data["current_age"],
            last_computed_age_date=datetime.now().date(),
            state=data["state"],
            country="USA",
            active=True
        )
        db_session.add(swimmer)
    
    db_session.commit()
    
    # Get the created swimmers
    swimmers = db_session.query(Swimmer).all()
    
    # Create sample teams
    teams = []
    
    team_data = [
        {"name": "High School A", "short_name": "HSA", "type": "high_school", "state": "CA"},
        {"name": "Swim Club B", "short_name": "SCB", "type": "club", "state": "TX"},
        {"name": "Academy C", "short_name": "ACA", "type": "high_school", "state": "FL"}
    ]
    
    for data in team_data:
        team = Team(
            name=data["name"],
            short_name=data["short_name"],
            type=data["type"],
            state=data["state"],
            country="USA",
            active=True
        )
        db_session.add(team)
    
    db_session.commit()
    
    # Get the created teams
    teams = db_session.query(Team).all()
    
    # Create sample swim times
    today = datetime.now().date()
    
    # For the first swimmer (John Smith) - 50 Freestyle progression
    times = [
        # Starting time from 2 years ago (slower)
        {"date": today - timedelta(days=730), "time": 27.50, "age": 15},
        # Gradual improvement
        {"date": today - timedelta(days=600), "time": 26.80, "age": 15},
        {"date": today - timedelta(days=500), "time": 26.20, "age": 16},
        {"date": today - timedelta(days=400), "time": 25.75, "age": 16},
        {"date": today - timedelta(days=300), "time": 25.30, "age": 16},
        {"date": today - timedelta(days=200), "time": 24.80, "age": 17},
        # Latest time (fastest)
        {"date": today - timedelta(days=30), "time": 24.40, "age": 17}
    ]
    
    for i, time_data in enumerate(times):
        time = SwimTime(
            swimmer_id=swimmers[0].id,
            event_id=events[0].id,  # 50 Freestyle
            team_id=teams[0].id,
            time_seconds=time_data["time"],
            time_formatted=str(time_data["time"]),
            date=time_data["date"],
            swimmer_age=time_data["age"],
            is_relay_leadoff=False,
            is_split=False,
            source="demo",
            source_id=f"demo-{i}",
            verified=True
        )
        db_session.add(time)
    
    # For the second swimmer (Jane Doe) - 100 Butterfly progression
    times = [
        # Starting time from 1.5 years ago (slower)
        {"date": today - timedelta(days=550), "time": 68.50, "age": 14},
        # Gradual improvement
        {"date": today - timedelta(days=450), "time": 67.20, "age": 15},
        {"date": today - timedelta(days=350), "time": 65.80, "age": 15},
        {"date": today - timedelta(days=250), "time": 64.50, "age": 15},
        # Latest time (fastest)
        {"date": today - timedelta(days=50), "time": 63.20, "age": 16}
    ]
    
    for i, time_data in enumerate(times):
        time = SwimTime(
            swimmer_id=swimmers[1].id,
            event_id=events[3].id,  # 100 Butterfly
            team_id=teams[1].id,
            time_seconds=time_data["time"],
            time_formatted=str(time_data["time"]),
            date=time_data["date"],
            swimmer_age=time_data["age"],
            is_relay_leadoff=False,
            is_split=False,
            source="demo",
            source_id=f"demo-butterfly-{i}",
            verified=True
        )
        db_session.add(time)
    
    # Create sample time standards
    standards_data = [
        # 50 Freestyle - Male
        {"event_id": events[0].id, "name": "State Cut", "gender": "M", "age_group": "15-16", "time": 25.00},
        {"event_id": events[0].id, "name": "National Cut", "gender": "M", "age_group": "15-16", "time": 23.50},
        {"event_id": events[0].id, "name": "Olympic Trials Cut", "gender": "M", "age_group": "Open", "time": 23.00},
        
        # 100 Butterfly - Female
        {"event_id": events[3].id, "name": "State Cut", "gender": "F", "age_group": "15-16", "time": 65.00},
        {"event_id": events[3].id, "name": "National Cut", "gender": "F", "age_group": "15-16", "time": 62.00},
        {"event_id": events[3].id, "name": "Olympic Trials Cut", "gender": "F", "age_group": "Open", "time": 60.50}
    ]
    
    for data in standards_data:
        standard = TimeStandard(
            event_id=data["event_id"],
            standard_name=data["name"],
            gender=data["gender"],
            age_group=data["age_group"],
            time_seconds=data["time"],
            time_formatted=str(data["time"]),
            season="2023-2024",
            source="demo"
        )
        db_session.add(standard)
    
    # Create sample records
    records_data = [
        # 50 Freestyle - Male National High School Record
        {
            "event_id": events[0].id,
            "type": "national_high_school",
            "gender": "M",
            "swimmer_name": "Top Swimmer",
            "team_name": "Fast High School",
            "time": 22.00,
            "date": today - timedelta(days=365)
        },
        # 50 Freestyle - Male State High School Record (CA)
        {
            "event_id": events[0].id,
            "type": "state_high_school",
            "scope": "CA",
            "gender": "M",
            "swimmer_name": "State Champion",
            "team_name": "State High School",
            "time": 22.50,
            "date": today - timedelta(days=730)
        },
        
        # 100 Butterfly - Female National High School Record
        {
            "event_id": events[3].id,
            "type": "national_high_school",
            "gender": "F",
            "swimmer_name": "Champion Swimmer",
            "team_name": "Elite Academy",
            "time": 59.00,
            "date": today - timedelta(days=180)
        },
        # 100 Butterfly - Female State High School Record (TX)
        {
            "event_id": events[3].id,
            "type": "state_high_school",
            "scope": "TX",
            "gender": "F",
            "swimmer_name": "Texas Champion",
            "team_name": "Texas High School",
            "time": 60.00,
            "date": today - timedelta(days=365)
        }
    ]
    
    for data in records_data:
        record = Record(
            event_id=data["event_id"],
            record_type=data["type"],
            scope=data.get("scope"),
            gender=data["gender"],
            swimmer_name=data["swimmer_name"],
            team_name=data["team_name"],
            time_seconds=data["time"],
            time_formatted=str(data["time"]),
            record_date=data["date"],
            source="demo",
            is_current=True
        )
        db_session.add(record)
    
    # Create more sample swim times for generating diverse statistics
    for swimmer in swimmers:
        for event in events:
            # Skip if we already created times for these specific combinations
            if (swimmer.id == swimmers[0].id and event.id == events[0].id) or \
               (swimmer.id == swimmers[1].id and event.id == events[3].id):
                continue
            
            # Create a random time appropriate for the event
            if event.distance == 50:
                base_time = 27.0
            elif event.distance == 100:
                base_time = 65.0
            elif event.distance == 200:
                base_time = 145.0
            else:
                base_time = 100.0
            
            # Add some randomness
            import random
            time_seconds = base_time + random.uniform(-5.0, 5.0)
            
            # Create the time
            time = SwimTime(
                swimmer_id=swimmer.id,
                event_id=event.id,
                team_id=teams[random.randint(0, len(teams)-1)].id,
                time_seconds=time_seconds,
                time_formatted=str(round(time_seconds, 2)),
                date=today - timedelta(days=random.randint(30, 365)),
                swimmer_age=swimmer.current_age,
                is_relay_leadoff=False,
                is_split=False,
                source="demo",
                source_id=f"demo-random-{swimmer.id}-{event.id}",
                verified=True
            )
            db_session.add(time)
    
    db_session.commit()
    
    return {
        "swimmers": [s.id for s in swimmers],
        "events": [e.id for e in events],
        "teams": [t.id for t in teams]
    }


def save_chart_to_file(chart_data, filename):
    """
    Save a base64 encoded chart to a file.
    
    Args:
        chart_data: Base64 encoded chart data
        filename: Output filename
        
    Returns:
        str: Path to saved file
    """
    import base64
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "chart_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output file path
    file_path = os.path.join(output_dir, filename)
    
    # Decode base64 data and write to file
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(chart_data))
    
    logger.info(f"Chart saved to {file_path}")
    return file_path


def demo_swimmer_progression(db_session, sample_data):
    """
    Demonstrate swimmer progression analysis and visualization.
    
    Args:
        db_session: Database session
        sample_data: Sample data IDs
    """
    logger.info("Demonstrating swimmer progression analysis...")
    
    # Get sample swimmer and event
    swimmer_id = sample_data["swimmers"][0]  # John Smith
    event_id = sample_data["events"][0]  # 50 Freestyle
    
    # Get progression data
    progression_data = calculate_progression(swimmer_id, event_id, db_session)
    logger.info(f"Progression data: {progression_data}")
    
    # Create progression chart
    chart_data = create_progression_chart(swimmer_id, event_id, db_session)
    save_chart_to_file(chart_data, "progression_chart.png")


def demo_standards_comparison(db_session, sample_data):
    """
    Demonstrate time standards comparison analysis and visualization.
    
    Args:
        db_session: Database session
        sample_data: Sample data IDs
    """
    logger.info("Demonstrating time standards comparison analysis...")
    
    # Get sample swimmer and event
    swimmer_id = sample_data["swimmers"][0]  # John Smith
    event_id = sample_data["events"][0]  # 50 Freestyle
    
    # Get standards comparison data
    comparison_data = compare_with_standards(swimmer_id, event_id, db_session)
    logger.info(f"Standards comparison data: {comparison_data}")
    
    # Create standards comparison chart
    chart_data = create_standards_comparison_chart(swimmer_id, event_id, db_session)
    save_chart_to_file(chart_data, "standards_comparison_chart.png")


def demo_elite_comparison(db_session, sample_data):
    """
    Demonstrate elite comparison analysis and visualization.
    
    Args:
        db_session: Database session
        sample_data: Sample data IDs
    """
    logger.info("Demonstrating elite comparison analysis...")
    
    # Get sample swimmer and event
    swimmer_id = sample_data["swimmers"][0]  # John Smith
    event_id = sample_data["events"][0]  # 50 Freestyle
    
    # Get elite comparison data
    comparison_data = compare_with_elite(swimmer_id, event_id, db_session)
    logger.info(f"Elite comparison data: {comparison_data}")
    
    # Create elite comparison chart
    chart_data = create_elite_comparison_chart(swimmer_id, event_id, db_session)
    save_chart_to_file(chart_data, "elite_comparison_chart.png")


def demo_peer_statistics(db_session, sample_data):
    """
    Demonstrate peer statistics analysis and visualization.
    
    Args:
        db_session: Database session
        sample_data: Sample data IDs
    """
    logger.info("Demonstrating peer statistics analysis...")
    
    # Get sample event
    event_id = sample_data["events"][0]  # 50 Freestyle
    
    # Get peer statistics for male swimmers in this event
    stats_data = get_peer_statistics(event_id, "M", 15, 18, None, db_session)
    logger.info(f"Peer statistics: {stats_data}")
    
    # Get sample swimmer for highlighting in the distribution
    swimmer_id = sample_data["swimmers"][0]  # John Smith
    
    # Create peer distribution chart
    chart_data = create_peer_distribution_chart(event_id, "M", 15, 18, None, 24.40, db_session)
    save_chart_to_file(chart_data, "peer_distribution_chart.png")


def demo_rankings(db_session, sample_data):
    """
    Demonstrate rankings analysis and visualization.
    
    Args:
        db_session: Database session
        sample_data: Sample data IDs
    """
    logger.info("Demonstrating rankings analysis...")
    
    # Get sample swimmer and event
    swimmer_id = sample_data["swimmers"][0]  # John Smith
    event_id = sample_data["events"][0]  # 50 Freestyle
    
    # Get rankings data
    rankings_data = calculate_rankings(swimmer_id, event_id, db_session)
    logger.info(f"Rankings data: {rankings_data}")
    
    # Create percentile chart
    chart_data = create_percentile_chart(swimmer_id, event_id, db_session)
    save_chart_to_file(chart_data, "percentile_chart.png")


def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description='Demo for swimming analytics')
    parser.add_argument('--reset-db', action='store_true', help='Reset the database and create sample data')
    parser.add_argument('--demo', choices=['all', 'progression', 'standards', 'elite', 'peers', 'rankings'],
                      default='all', help='Specific demo to run')
    
    args = parser.parse_args()
    
    # Create a database session
    db_session = SessionLocal()
    
    try:
        sample_data = None
        
        # Reset database and create sample data if requested
        if args.reset_db:
            # Recreate tables
            from database.models import Base
            from sqlalchemy import create_engine
            from database.database import SQLALCHEMY_DATABASE_URL
            
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            
            # Drop all tables
            Base.metadata.drop_all(bind=engine)
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            
            # Create sample data
            sample_data = create_sample_data(db_session)
        else:
            # Get existing sample data IDs
            swimmers = db_session.query(Swimmer).all()
            events = db_session.query(Event).all()
            teams = db_session.query(Team).all()
            
            if not swimmers or not events or not teams:
                logger.error("No sample data found. Please run with --reset-db to create sample data.")
                return
            
            sample_data = {
                "swimmers": [s.id for s in swimmers],
                "events": [e.id for e in events],
                "teams": [t.id for t in teams]
            }
        
        # Run the requested demo
        if args.demo == 'all' or args.demo == 'progression':
            demo_swimmer_progression(db_session, sample_data)
        
        if args.demo == 'all' or args.demo == 'standards':
            demo_standards_comparison(db_session, sample_data)
        
        if args.demo == 'all' or args.demo == 'elite':
            demo_elite_comparison(db_session, sample_data)
        
        if args.demo == 'all' or args.demo == 'peers':
            demo_peer_statistics(db_session, sample_data)
        
        if args.demo == 'all' or args.demo == 'rankings':
            demo_rankings(db_session, sample_data)
        
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
