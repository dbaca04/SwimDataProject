"""
API Models

This module defines the Pydantic models used for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class SwimmerBase(BaseModel):
    """Base model for swimmer data."""
    primary_name: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    current_age: Optional[int] = None
    state: Optional[str] = None
    country: Optional[str] = 'USA'


class SwimmerCreate(SwimmerBase):
    """Model for creating a new swimmer."""
    pass


class SwimmerUpdate(SwimmerBase):
    """Model for updating a swimmer."""
    primary_name: Optional[str] = None


class SwimmerResponse(SwimmerBase):
    """Model for swimmer response."""
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TeamBase(BaseModel):
    """Base model for team data."""
    name: str
    short_name: Optional[str] = None
    type: str  # 'high_school', 'club', 'college', etc.
    state: Optional[str] = None
    country: Optional[str] = 'USA'


class TeamCreate(TeamBase):
    """Model for creating a new team."""
    pass


class TeamUpdate(TeamBase):
    """Model for updating a team."""
    name: Optional[str] = None
    type: Optional[str] = None


class TeamResponse(TeamBase):
    """Model for team response."""
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    """Base model for event data."""
    name: str
    distance: int
    stroke: str  # 'freestyle', 'backstroke', etc.
    course: str  # 'SCY', 'SCM', 'LCM'
    is_relay: bool = False
    standard_name: str


class EventCreate(EventBase):
    """Model for creating a new event."""
    pass


class EventUpdate(EventBase):
    """Model for updating an event."""
    name: Optional[str] = None
    distance: Optional[int] = None
    stroke: Optional[str] = None
    course: Optional[str] = None
    is_relay: Optional[bool] = None
    standard_name: Optional[str] = None


class EventResponse(EventBase):
    """Model for event response."""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MeetBase(BaseModel):
    """Base model for meet data."""
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    course: Optional[str] = None  # 'SCY', 'SCM', 'LCM'
    host: Optional[str] = None
    meet_type: Optional[str] = None  # 'high_school', 'club', 'championship', etc.
    is_observed: bool = False
    source: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None


class MeetCreate(MeetBase):
    """Model for creating a new meet."""
    pass


class MeetUpdate(MeetBase):
    """Model for updating a meet."""
    name: Optional[str] = None


class MeetResponse(MeetBase):
    """Model for meet response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TimeBase(BaseModel):
    """Base model for swim time data."""
    swimmer_id: int
    event_id: int
    meet_id: Optional[int] = None
    team_id: Optional[int] = None
    time_seconds: float
    time_formatted: str
    date: date
    swimmer_age: Optional[int] = None
    is_relay_leadoff: bool = False
    is_split: bool = False
    source: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    verified: bool = False


class TimeCreate(TimeBase):
    """Model for creating a new swim time."""
    pass


class TimeUpdate(TimeBase):
    """Model for updating a swim time."""
    swimmer_id: Optional[int] = None
    event_id: Optional[int] = None
    meet_id: Optional[int] = None
    team_id: Optional[int] = None
    time_seconds: Optional[float] = None
    time_formatted: Optional[str] = None
    date: Optional[date] = None
    swimmer_age: Optional[int] = None
    is_relay_leadoff: Optional[bool] = None
    is_split: Optional[bool] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    verified: Optional[bool] = None


class TimeResponse(TimeBase):
    """Model for swim time response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Include related objects
    swimmer: Optional[SwimmerResponse] = None
    event: Optional[EventResponse] = None
    meet: Optional[MeetResponse] = None
    team: Optional[TeamResponse] = None

    class Config:
        orm_mode = True


class RankingBase(BaseModel):
    """Base model for ranking data."""
    swimmer_id: int
    event_id: int
    time_id: Optional[int] = None
    rank: int
    time_seconds: float
    rank_scope: str  # 'national', 'state', 'age_group', etc.
    rank_scope_value: Optional[str] = None  # For state: 'CA', for age_group: '15-16', etc.
    season: Optional[str] = None  # '2023-2024', etc.
    as_of_date: date
    source: str
    source_id: Optional[str] = None


class RankingCreate(RankingBase):
    """Model for creating a new ranking."""
    pass


class RankingUpdate(RankingBase):
    """Model for updating a ranking."""
    swimmer_id: Optional[int] = None
    event_id: Optional[int] = None
    time_id: Optional[int] = None
    rank: Optional[int] = None
    time_seconds: Optional[float] = None
    rank_scope: Optional[str] = None
    rank_scope_value: Optional[str] = None
    season: Optional[str] = None
    as_of_date: Optional[date] = None
    source: Optional[str] = None
    source_id: Optional[str] = None


class RankingResponse(RankingBase):
    """Model for ranking response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Include related objects
    swimmer: Optional[SwimmerResponse] = None
    event: Optional[EventResponse] = None

    class Config:
        orm_mode = True


class TimeStandardBase(BaseModel):
    """Base model for time standard data."""
    event_id: int
    standard_name: str  # 'AAAA', 'AAA', 'AA', etc. or 'Futures', 'Junior National', etc.
    gender: str
    age_group: str  # '11-12', '13-14', '15-16', '17-18', 'Open', etc.
    time_seconds: float
    time_formatted: str
    season: Optional[str] = None  # '2023-2024', etc.
    source: str


class TimeStandardCreate(TimeStandardBase):
    """Model for creating a new time standard."""
    pass


class TimeStandardUpdate(TimeStandardBase):
    """Model for updating a time standard."""
    event_id: Optional[int] = None
    standard_name: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    time_seconds: Optional[float] = None
    time_formatted: Optional[str] = None
    season: Optional[str] = None
    source: Optional[str] = None


class TimeStandardResponse(TimeStandardBase):
    """Model for time standard response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Include related objects
    event: Optional[EventResponse] = None

    class Config:
        orm_mode = True
