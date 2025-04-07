"""
Database Models

This module defines the SQLAlchemy ORM models for the database.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Swimmer(Base):
    """Swimmer model representing an individual swimmer."""
    __tablename__ = 'swimmers'
    
    id = Column(Integer, primary_key=True)
    primary_name = Column(String(255), nullable=False)
    gender = Column(String(1))  # 'M', 'F', or 'O'
    birth_year = Column(Integer)
    current_age = Column(Integer)
    last_computed_age_date = Column(Date)
    state = Column(String(50))
    country = Column(String(50), default='USA')
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    aliases = relationship("SwimmerAlias", back_populates="swimmer")
    team_affiliations = relationship("SwimmerTeamAffiliation", back_populates="swimmer")
    times = relationship("SwimTime", back_populates="swimmer")
    rankings = relationship("Ranking", back_populates="swimmer")


class SwimmerAlias(Base):
    """Model for swimmer name variations across different sources."""
    __tablename__ = 'swimmer_aliases'
    
    id = Column(Integer, primary_key=True)
    swimmer_id = Column(Integer, ForeignKey('swimmers.id', ondelete='CASCADE'), nullable=False)
    name_alias = Column(String(255), nullable=False)
    source = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    swimmer = relationship("Swimmer", back_populates="aliases")
    
    __table_args__ = {'sqlite_autoincrement': True}


class Team(Base):
    """Model for swimming teams/schools."""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    type = Column(String(50), nullable=False)  # 'high_school', 'club', 'college', etc.
    state = Column(String(50))
    country = Column(String(50), default='USA')
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    aliases = relationship("TeamAlias", back_populates="team")
    swimmer_affiliations = relationship("SwimmerTeamAffiliation", back_populates="team")
    times = relationship("SwimTime", back_populates="team")


class TeamAlias(Base):
    """Model for team name variations across different sources."""
    __tablename__ = 'team_aliases'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    name_alias = Column(String(255), nullable=False)
    source = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="aliases")
    
    __table_args__ = {'sqlite_autoincrement': True}


class SwimmerTeamAffiliation(Base):
    """Model for a swimmer's affiliation with a team over time."""
    __tablename__ = 'swimmer_team_affiliations'
    
    id = Column(Integer, primary_key=True)
    swimmer_id = Column(Integer, ForeignKey('swimmers.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=True)
    source = Column(String(100))
    source_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swimmer = relationship("Swimmer", back_populates="team_affiliations")
    team = relationship("Team", back_populates="swimmer_affiliations")


class Event(Base):
    """Model for swimming events."""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    distance = Column(Integer, nullable=False)
    stroke = Column(String(50), nullable=False)  # 'freestyle', 'backstroke', etc.
    course = Column(String(10), nullable=False)  # 'SCY', 'SCM', 'LCM'
    is_relay = Column(Boolean, default=False)
    standard_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    aliases = relationship("EventAlias", back_populates="event")
    times = relationship("SwimTime", back_populates="event")
    rankings = relationship("Ranking", back_populates="event")
    time_standards = relationship("TimeStandard", back_populates="event")


class EventAlias(Base):
    """Model for event name variations across different sources."""
    __tablename__ = 'event_aliases'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    name_alias = Column(String(255), nullable=False)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="aliases")
    
    __table_args__ = {'sqlite_autoincrement': True}


class Meet(Base):
    """Model for swimming meets/competitions."""
    __tablename__ = 'meets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    location = Column(String(255))
    course = Column(String(10))  # 'SCY', 'SCM', 'LCM'
    host = Column(String(255))
    meet_type = Column(String(100))  # 'high_school', 'club', 'championship', etc.
    is_observed = Column(Boolean, default=False)
    source = Column(String(100))
    source_id = Column(String(100))
    source_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    times = relationship("SwimTime", back_populates="meet")


class SwimTime(Base):
    """Model for individual swim times."""
    __tablename__ = 'swim_times'
    
    id = Column(Integer, primary_key=True)
    swimmer_id = Column(Integer, ForeignKey('swimmers.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    meet_id = Column(Integer, ForeignKey('meets.id', ondelete='SET NULL'))
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'))
    time_seconds = Column(Numeric(10, 2), nullable=False)
    time_formatted = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    swimmer_age = Column(Integer)
    is_relay_leadoff = Column(Boolean, default=False)
    is_split = Column(Boolean, default=False)
    source = Column(String(100), nullable=False)
    source_id = Column(String(100))
    source_url = Column(Text)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swimmer = relationship("Swimmer", back_populates="times")
    event = relationship("Event", back_populates="times")
    meet = relationship("Meet", back_populates="times")
    team = relationship("Team", back_populates="times")
    rankings = relationship("Ranking", back_populates="time")


class Ranking(Base):
    """Model for swimmer rankings."""
    __tablename__ = 'rankings'
    
    id = Column(Integer, primary_key=True)
    swimmer_id = Column(Integer, ForeignKey('swimmers.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    time_id = Column(Integer, ForeignKey('swim_times.id', ondelete='CASCADE'))
    rank = Column(Integer, nullable=False)
    time_seconds = Column(Numeric(10, 2), nullable=False)
    rank_scope = Column(String(50), nullable=False)  # 'national', 'state', 'age_group', etc.
    rank_scope_value = Column(String(100))  # For state: 'CA', for age_group: '15-16', etc.
    season = Column(String(20))  # '2023-2024', etc.
    as_of_date = Column(Date, nullable=False)
    source = Column(String(100), nullable=False)
    source_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swimmer = relationship("Swimmer", back_populates="rankings")
    event = relationship("Event", back_populates="rankings")
    time = relationship("SwimTime", back_populates="rankings")


class TimeStandard(Base):
    """Model for swimming time standards."""
    __tablename__ = 'time_standards'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    standard_name = Column(String(100), nullable=False)  # 'AAAA', 'AAA', 'AA', etc. or 'Futures', 'Junior National', etc.
    gender = Column(String(1), nullable=False)
    age_group = Column(String(20), nullable=False)  # '11-12', '13-14', '15-16', '17-18', 'Open', etc.
    time_seconds = Column(Numeric(10, 2), nullable=False)
    time_formatted = Column(String(20), nullable=False)
    season = Column(String(20))  # '2023-2024', etc.
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="time_standards")


class DataSource(Base):
    """Model for tracking information about data sources."""
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255))
    description = Column(Text)
    last_scraped = Column(DateTime)
    scrape_frequency = Column(String(50))  # 'daily', 'weekly', 'monthly', etc.
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SourceMapping(Base):
    """Model for mapping IDs between external sources and internal entities."""
    __tablename__ = 'source_mapping'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(100), nullable=False)
    source_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'swimmer', 'team', 'meet', etc.
    entity_id = Column(Integer, nullable=False)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
