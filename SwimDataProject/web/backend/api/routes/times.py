"""
Times Routes

This module contains API routes for swim time data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from database.database import get_db_session
from database.models import SwimTime as DbSwimTime
from web.backend.api.models import TimeResponse, TimeCreate, TimeUpdate

router = APIRouter()


@router.get("", response_model=List[TimeResponse])
def get_times(
    skip: int = 0,
    limit: int = 100,
    swimmer_id: Optional[int] = None,
    event_id: Optional[int] = None,
    team_id: Optional[int] = None,
    meet_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_time: Optional[float] = None,
    max_time: Optional[float] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of swim times with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        swimmer_id: Filter by swimmer ID
        event_id: Filter by event ID
        team_id: Filter by team ID
        meet_id: Filter by meet ID
        start_date: Filter by minimum date
        end_date: Filter by maximum date
        min_time: Filter by minimum time (in seconds)
        max_time: Filter by maximum time (in seconds)
        db: Database session
        
    Returns:
        List[TimeResponse]: List of swim times
    """
    query = db.query(DbSwimTime)
    
    # Apply filters
    if swimmer_id:
        query = query.filter(DbSwimTime.swimmer_id == swimmer_id)
    if event_id:
        query = query.filter(DbSwimTime.event_id == event_id)
    if team_id:
        query = query.filter(DbSwimTime.team_id == team_id)
    if meet_id:
        query = query.filter(DbSwimTime.meet_id == meet_id)
    if start_date:
        query = query.filter(DbSwimTime.date >= start_date)
    if end_date:
        query = query.filter(DbSwimTime.date <= end_date)
    if min_time is not None:
        query = query.filter(DbSwimTime.time_seconds >= min_time)
    if max_time is not None:
        query = query.filter(DbSwimTime.time_seconds <= max_time)
    
    # Order by date (most recent first)
    query = query.order_by(DbSwimTime.date.desc())
    
    return query.offset(skip).limit(limit).all()


@router.get("/{time_id}", response_model=TimeResponse)
def get_time(time_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific swim time by ID.
    
    Args:
        time_id: ID of the swim time
        db: Database session
        
    Returns:
        TimeResponse: Swim time data
        
    Raises:
        HTTPException: If swim time not found
    """
    time = db.query(DbSwimTime).filter(DbSwimTime.id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Swim time not found")
    return time


@router.post("", response_model=TimeResponse, status_code=201)
def create_time(time: TimeCreate, db: Session = Depends(get_db_session)):
    """
    Create a new swim time.
    
    Args:
        time: Swim time data
        db: Database session
        
    Returns:
        TimeResponse: Created swim time data
    """
    db_time = DbSwimTime(
        swimmer_id=time.swimmer_id,
        event_id=time.event_id,
        meet_id=time.meet_id,
        team_id=time.team_id,
        time_seconds=time.time_seconds,
        time_formatted=time.time_formatted,
        date=time.date,
        swimmer_age=time.swimmer_age,
        is_relay_leadoff=time.is_relay_leadoff,
        is_split=time.is_split,
        source=time.source,
        source_id=time.source_id,
        source_url=time.source_url,
        verified=time.verified
    )
    db.add(db_time)
    db.commit()
    db.refresh(db_time)
    return db_time


@router.put("/{time_id}", response_model=TimeResponse)
def update_time(
    time_id: int,
    time: TimeUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update a swim time.
    
    Args:
        time_id: ID of the swim time to update
        time: Updated swim time data
        db: Database session
        
    Returns:
        TimeResponse: Updated swim time data
        
    Raises:
        HTTPException: If swim time not found
    """
    db_time = db.query(DbSwimTime).filter(DbSwimTime.id == time_id).first()
    if not db_time:
        raise HTTPException(status_code=404, detail="Swim time not found")
    
    # Update fields if provided
    update_data = time.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_time, key, value)
    
    db.commit()
    db.refresh(db_time)
    return db_time


@router.delete("/{time_id}", status_code=204)
def delete_time(time_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a swim time.
    
    Args:
        time_id: ID of the swim time to delete
        db: Database session
        
    Raises:
        HTTPException: If swim time not found
    """
    db_time = db.query(DbSwimTime).filter(DbSwimTime.id == time_id).first()
    if not db_time:
        raise HTTPException(status_code=404, detail="Swim time not found")
    
    db.delete(db_time)
    db.commit()
    return None


@router.get("/personal-bests/{swimmer_id}", response_model=List[TimeResponse])
def get_personal_bests(
    swimmer_id: int,
    event_id: Optional[int] = None,
    course: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a swimmer's personal best times.
    
    Args:
        swimmer_id: ID of the swimmer
        event_id: Optional filter by event ID
        course: Optional filter by course type ('SCY', 'SCM', 'LCM')
        db: Database session
        
    Returns:
        List[TimeResponse]: List of personal best times
    """
    from sqlalchemy import func
    from database.models import Event
    
    # Subquery to get the minimum time for each event
    subquery = (
        db.query(
            DbSwimTime.event_id,
            func.min(DbSwimTime.time_seconds).label('min_time')
        )
        .filter(DbSwimTime.swimmer_id == swimmer_id)
        .group_by(DbSwimTime.event_id)
        .subquery()
    )
    
    # Main query to get the actual times
    query = (
        db.query(DbSwimTime)
        .join(
            subquery,
            (DbSwimTime.event_id == subquery.c.event_id) & 
            (DbSwimTime.time_seconds == subquery.c.min_time)
        )
        .filter(DbSwimTime.swimmer_id == swimmer_id)
    )
    
    # Apply additional filters
    if event_id:
        query = query.filter(DbSwimTime.event_id == event_id)
    
    if course:
        query = query.join(Event).filter(Event.course == course)
    
    return query.all()
