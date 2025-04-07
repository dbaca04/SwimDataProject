"""
Swimmers Routes

This module contains API routes for swimmer data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from database.database import get_db_session
from database.models import Swimmer as DbSwimmer
from web.backend.api.models import SwimmerResponse, SwimmerCreate, SwimmerUpdate

router = APIRouter()


@router.get("", response_model=List[SwimmerResponse])
def get_swimmers(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    state: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of swimmers with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        name: Filter by name (partial match)
        gender: Filter by gender
        state: Filter by state
        min_age: Filter by minimum age
        max_age: Filter by maximum age
        db: Database session
        
    Returns:
        List[SwimmerResponse]: List of swimmers
    """
    query = db.query(DbSwimmer)
    
    # Apply filters
    if name:
        query = query.filter(DbSwimmer.primary_name.ilike(f"%{name}%"))
    if gender:
        query = query.filter(DbSwimmer.gender == gender)
    if state:
        query = query.filter(DbSwimmer.state == state)
    if min_age is not None:
        query = query.filter(DbSwimmer.current_age >= min_age)
    if max_age is not None:
        query = query.filter(DbSwimmer.current_age <= max_age)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{swimmer_id}", response_model=SwimmerResponse)
def get_swimmer(swimmer_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific swimmer by ID.
    
    Args:
        swimmer_id: ID of the swimmer
        db: Database session
        
    Returns:
        SwimmerResponse: Swimmer data
        
    Raises:
        HTTPException: If swimmer not found
    """
    swimmer = db.query(DbSwimmer).filter(DbSwimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    return swimmer


@router.post("", response_model=SwimmerResponse, status_code=201)
def create_swimmer(swimmer: SwimmerCreate, db: Session = Depends(get_db_session)):
    """
    Create a new swimmer.
    
    Args:
        swimmer: Swimmer data
        db: Database session
        
    Returns:
        SwimmerResponse: Created swimmer data
    """
    db_swimmer = DbSwimmer(
        primary_name=swimmer.primary_name,
        gender=swimmer.gender,
        birth_year=swimmer.birth_year,
        current_age=swimmer.current_age,
        state=swimmer.state,
        country=swimmer.country
    )
    db.add(db_swimmer)
    db.commit()
    db.refresh(db_swimmer)
    return db_swimmer


@router.put("/{swimmer_id}", response_model=SwimmerResponse)
def update_swimmer(
    swimmer_id: int,
    swimmer: SwimmerUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update a swimmer's information.
    
    Args:
        swimmer_id: ID of the swimmer to update
        swimmer: Updated swimmer data
        db: Database session
        
    Returns:
        SwimmerResponse: Updated swimmer data
        
    Raises:
        HTTPException: If swimmer not found
    """
    db_swimmer = db.query(DbSwimmer).filter(DbSwimmer.id == swimmer_id).first()
    if not db_swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    # Update fields if provided
    update_data = swimmer.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_swimmer, key, value)
    
    db.commit()
    db.refresh(db_swimmer)
    return db_swimmer


@router.delete("/{swimmer_id}", status_code=204)
def delete_swimmer(swimmer_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a swimmer.
    
    Args:
        swimmer_id: ID of the swimmer to delete
        db: Database session
        
    Raises:
        HTTPException: If swimmer not found
    """
    db_swimmer = db.query(DbSwimmer).filter(DbSwimmer.id == swimmer_id).first()
    if not db_swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    db.delete(db_swimmer)
    db.commit()
    return None
