"""
Unit tests for database models.

These tests verify that ORM models are correctly defined and relationships work as expected.
"""
import pytest
import os
import sys
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the models
from database.models import (
    Base, Swimmer, Team, Event, SwimTime, Ranking, 
    TimeStandard, Record, SwimmerTeamAffiliation
)


@pytest.fixture(scope="module")
def test_db():
    """Create an in-memory database for testing."""
    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create a session factory
    SessionFactory = sessionmaker(bind=engine)
    
    # Create a session
    session = SessionFactory()
    
    # Return the session
    yield session
    
    # Clean up
    session.close()


class TestDatabaseModels:
    """Tests for database models."""
    
    def test_swimmer_model(self, test_db):
        """Test Swimmer model creation and relationships."""
        # Create a swimmer
        swimmer = Swimmer(
            primary_name="John Doe",
            gender="M",
            birth_year=2008,
            current_age=17,
            last_computed_age_date=datetime.date.today(),
            state="CA",
            country="USA",
            active=True
        )
        
        # Add to database
        test_db.add(swimmer)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(Swimmer).filter_by(primary_name="John Doe").first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.primary_name == "John Doe"
        assert retrieved.gender == "M"
        assert retrieved.birth_year == 2008
        assert retrieved.current_age == 17
        assert retrieved.state == "CA"
        assert retrieved.country == "USA"
        assert retrieved.active == True
        
        # Verify auto fields
        assert retrieved.id is not None
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
    
    def test_team_model(self, test_db):
        """Test Team model creation and relationships."""
        # Create a team
        team = Team(
            name="Example High School",
            short_name="EHS",
            type="high_school",
            state="CA",
            country="USA",
            active=True
        )
        
        # Add to database
        test_db.add(team)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(Team).filter_by(name="Example High School").first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.name == "Example High School"
        assert retrieved.short_name == "EHS"
        assert retrieved.type == "high_school"
        assert retrieved.state == "CA"
        assert retrieved.country == "USA"
        assert retrieved.active == True
        
        # Verify auto fields
        assert retrieved.id is not None
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
    
    def test_event_model(self, test_db):
        """Test Event model creation and relationships."""
        # Create an event
        event = Event(
            name="100 Freestyle",
            distance=100,
            stroke="Freestyle",
            course="SCY",
            is_relay=False,
            standard_name="100 Freestyle"
        )
        
        # Add to database
        test_db.add(event)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(Event).filter_by(name="100 Freestyle").first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.name == "100 Freestyle"
        assert retrieved.distance == 100
        assert retrieved.stroke == "Freestyle"
        assert retrieved.course == "SCY"
        assert retrieved.is_relay == False
        assert retrieved.standard_name == "100 Freestyle"
        
        # Verify auto fields
        assert retrieved.id is not None
        assert retrieved.created_at is not None
    
    def test_swimmer_team_relationship(self, test_db):
        """Test the relationship between swimmers and teams."""
        # Get existing swimmer and team
        swimmer = test_db.query(Swimmer).first()
        team = test_db.query(Team).first()
        
        # Create affiliation
        affiliation = SwimmerTeamAffiliation(
            swimmer_id=swimmer.id,
            team_id=team.id,
            start_date=datetime.date(2023, 9, 1),
            end_date=datetime.date(2024, 6, 30),
            is_current=True,
            source="test",
            source_id="test123"
        )
        
        # Add to database
        test_db.add(affiliation)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(SwimmerTeamAffiliation).filter_by(
            swimmer_id=swimmer.id, team_id=team.id
        ).first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.swimmer_id == swimmer.id
        assert retrieved.team_id == team.id
        assert retrieved.start_date == datetime.date(2023, 9, 1)
        assert retrieved.end_date == datetime.date(2024, 6, 30)
        assert retrieved.is_current == True
        
        # Test relationships
        assert retrieved.swimmer.primary_name == swimmer.primary_name
        assert retrieved.team.name == team.name
    
    def test_swim_time_model(self, test_db):
        """Test SwimTime model creation and relationships."""
        # Get existing swimmer and event
        swimmer = test_db.query(Swimmer).first()
        event = test_db.query(Event).first()
        team = test_db.query(Team).first()
        
        # Create a swim time
        swim_time = SwimTime(
            swimmer_id=swimmer.id,
            event_id=event.id,
            team_id=team.id,
            time_seconds=50.25,
            time_formatted="50.25",
            date=datetime.date(2024, 3, 15),
            swimmer_age=16,
            is_relay_leadoff=False,
            is_split=False,
            source="test",
            source_id="time123",
            verified=True
        )
        
        # Add to database
        test_db.add(swim_time)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(SwimTime).filter_by(
            swimmer_id=swimmer.id, event_id=event.id, time_seconds=50.25
        ).first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.swimmer_id == swimmer.id
        assert retrieved.event_id == event.id
        assert retrieved.team_id == team.id
        assert retrieved.time_seconds == 50.25
        assert retrieved.time_formatted == "50.25"
        assert retrieved.date == datetime.date(2024, 3, 15)
        assert retrieved.swimmer_age == 16
        assert retrieved.is_relay_leadoff == False
        assert retrieved.is_split == False
        assert retrieved.source == "test"
        assert retrieved.source_id == "time123"
        assert retrieved.verified == True
        
        # Test relationships
        assert retrieved.swimmer.primary_name == swimmer.primary_name
        assert retrieved.event.name == event.name
        assert retrieved.team.name == team.name
    
    def test_ranking_model(self, test_db):
        """Test Ranking model creation and relationships."""
        # Get existing swimmer and event
        swimmer = test_db.query(Swimmer).first()
        event = test_db.query(Event).first()
        swim_time = test_db.query(SwimTime).first()
        
        # Create a ranking
        ranking = Ranking(
            swimmer_id=swimmer.id,
            event_id=event.id,
            time_id=swim_time.id,
            rank=1,
            time_seconds=50.25,
            rank_scope="state",
            rank_scope_value="CA",
            season="2023-2024",
            as_of_date=datetime.date(2024, 3, 20),
            source="test",
            source_id="ranking123"
        )
        
        # Add to database
        test_db.add(ranking)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(Ranking).filter_by(
            swimmer_id=swimmer.id, event_id=event.id, rank=1
        ).first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.swimmer_id == swimmer.id
        assert retrieved.event_id == event.id
        assert retrieved.time_id == swim_time.id
        assert retrieved.rank == 1
        assert retrieved.time_seconds == 50.25
        assert retrieved.rank_scope == "state"
        assert retrieved.rank_scope_value == "CA"
        assert retrieved.season == "2023-2024"
        assert retrieved.as_of_date == datetime.date(2024, 3, 20)
        assert retrieved.source == "test"
        assert retrieved.source_id == "ranking123"
        
        # Test relationships
        assert retrieved.swimmer.primary_name == swimmer.primary_name
        assert retrieved.event.name == event.name
        assert retrieved.time.time_seconds == swim_time.time_seconds
    
    def test_time_standard_model(self, test_db):
        """Test TimeStandard model creation and relationships."""
        # Get existing event
        event = test_db.query(Event).first()
        
        # Create a time standard
        time_standard = TimeStandard(
            event_id=event.id,
            standard_name="State Cut",
            gender="M",
            age_group="15-16",
            time_seconds=52.5,
            time_formatted="52.50",
            season="2023-2024",
            source="test"
        )
        
        # Add to database
        test_db.add(time_standard)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(TimeStandard).filter_by(
            event_id=event.id, standard_name="State Cut", gender="M"
        ).first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.event_id == event.id
        assert retrieved.standard_name == "State Cut"
        assert retrieved.gender == "M"
        assert retrieved.age_group == "15-16"
        assert retrieved.time_seconds == 52.5
        assert retrieved.time_formatted == "52.50"
        assert retrieved.season == "2023-2024"
        assert retrieved.source == "test"
        
        # Test relationships
        assert retrieved.event.name == event.name
    
    def test_record_model(self, test_db):
        """Test Record model creation and relationships."""
        # Get existing event and swimmer
        event = test_db.query(Event).first()
        swimmer = test_db.query(Swimmer).first()
        
        # Create a record
        record = Record(
            event_id=event.id,
            record_type="state_high_school",
            scope="CA",
            gender="M",
            swimmer_id=swimmer.id,
            swimmer_name=swimmer.primary_name,
            team_name="Example High School",
            time_seconds=48.75,
            time_formatted="48.75",
            record_date=datetime.date(2024, 2, 10),
            source="test",
            is_current=True
        )
        
        # Add to database
        test_db.add(record)
        test_db.commit()
        
        # Query to verify
        retrieved = test_db.query(Record).filter_by(
            event_id=event.id, record_type="state_high_school", gender="M"
        ).first()
        
        # Verify fields
        assert retrieved is not None
        assert retrieved.event_id == event.id
        assert retrieved.record_type == "state_high_school"
        assert retrieved.scope == "CA"
        assert retrieved.gender == "M"
        assert retrieved.swimmer_id == swimmer.id
        assert retrieved.swimmer_name == swimmer.primary_name
        assert retrieved.team_name == "Example High School"
        assert retrieved.time_seconds == 48.75
        assert retrieved.time_formatted == "48.75"
        assert retrieved.record_date == datetime.date(2024, 2, 10)
        assert retrieved.source == "test"
        assert retrieved.is_current == True
        
        # Test relationships
        assert retrieved.event.name == event.name
        assert retrieved.swimmer.primary_name == swimmer.primary_name


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
