"""
Events Routes

This module contains API routes for event data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from database.database import get_db_session
from database.models import Event as DbEvent
from web.backend.api.models import EventResponse, EventCreate, EventUpdate

router = APIRouter()


@router.get("", response_model=List[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    distance: Optional[int] = None,
    stroke: Optional[str] = None,
    course: Optional[str] = None,
    is_relay: Optional[bool] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of events with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        distance: Filter by distance
        stroke: Filter by stroke
        course: Filter by course type
        is_relay: Filter by relay status
        db: Database session
        
    Returns:
        List[EventResponse]: List of events
    """
    query = db.query(DbEvent)
    
    # Apply filters
    if distance:
        query = query.filter(DbEvent.distance == distance)
    if stroke:
        query = query.filter(DbEvent.stroke == stroke)
    if course:
        query = query.filter(DbEvent.course == course)
    if is_relay is not None:
        query = query.filter(DbEvent.is_relay == is_relay)
    
    # Order by distance and stroke
    query = query.order_by(DbEvent.course, DbEvent.distance, DbEvent.stroke)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific event by ID.
    
    Args:
        event_id: ID of the event
        db: Database session
        
    Returns:
        EventResponse: Event data
        
    Raises:
        HTTPException: If event not found
    """
    event = db.query(DbEvent).filter(DbEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db_session)):
    """
    Create a new event.
    
    Args:
        event: Event data
        db: Database session
        
    Returns:
        EventResponse: Created event data
    """
    db_event = DbEvent(
        name=event.name,
        distance=event.distance,
        stroke=event.stroke,
        course=event.course,
        is_relay=event.is_relay,
        standard_name=event.standard_name
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update an event.
    
    Args:
        event_id: ID of the event to update
        event: Updated event data
        db: Database session
        
    Returns:
        EventResponse: Updated event data
        
    Raises:
        HTTPException: If event not found
    """
    db_event = db.query(DbEvent).filter(DbEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update fields if provided
    update_data = event.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db_session)):
    """
    Delete an event.
    
    Args:
        event_id: ID of the event to delete
        db: Database session
        
    Raises:
        HTTPException: If event not found
    """
    db_event = db.query(DbEvent).filter(DbEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return None


@router.get("/by-name/{standard_name}", response_model=EventResponse)
def get_event_by_name(standard_name: str, db: Session = Depends(get_db_session)):
    """
    Get an event by its standard name.
    
    Args:
        standard_name: Standard name of the event
        db: Database session
        
    Returns:
        EventResponse: Event data
        
    Raises:
        HTTPException: If event not found
    """
    event = db.query(DbEvent).filter(DbEvent.standard_name == standard_name).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/alias/{alias_name}", response_model=EventResponse)
def get_event_by_alias(alias_name: str, db: Session = Depends(get_db_session)):
    """
    Get an event by an alias name.
    
    Args:
        alias_name: Alias name to look up
        db: Database session
        
    Returns:
        EventResponse: Event data
        
    Raises:
        HTTPException: If event not found
    """
    from database.models import EventAlias
    
    # Look up the event through the alias
    alias = db.query(EventAlias).filter(EventAlias.name_alias == alias_name).first()
    if not alias:
        raise HTTPException(status_code=404, detail="Event alias not found")
    
    # Get the event
    event = db.query(DbEvent).filter(DbEvent.id == alias.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event
