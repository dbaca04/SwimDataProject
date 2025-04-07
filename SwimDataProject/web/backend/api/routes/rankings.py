"""
Rankings Routes

This module contains API routes for swimmer rankings data.
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
from database.models import Ranking as DbRanking
from web.backend.api.models import RankingResponse, RankingCreate, RankingUpdate

router = APIRouter()


@router.get("", response_model=List[RankingResponse])
def get_rankings(
    skip: int = 0,
    limit: int = 100,
    swimmer_id: Optional[int] = None,
    event_id: Optional[int] = None,
    rank_scope: Optional[str] = None,
    rank_scope_value: Optional[str] = None,
    season: Optional[str] = None,
    max_rank: Optional[int] = None,
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of rankings with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        swimmer_id: Filter by swimmer ID
        event_id: Filter by event ID
        rank_scope: Filter by ranking scope (e.g., 'national', 'state')
        rank_scope_value: Filter by ranking scope value (e.g., state code)
        season: Filter by season
        max_rank: Filter by maximum rank
        as_of_date: Filter by ranking date
        db: Database session
        
    Returns:
        List[RankingResponse]: List of rankings
    """
    query = db.query(DbRanking)
    
    # Apply filters
    if swimmer_id:
        query = query.filter(DbRanking.swimmer_id == swimmer_id)
    if event_id:
        query = query.filter(DbRanking.event_id == event_id)
    if rank_scope:
        query = query.filter(DbRanking.rank_scope == rank_scope)
    if rank_scope_value:
        query = query.filter(DbRanking.rank_scope_value == rank_scope_value)
    if season:
        query = query.filter(DbRanking.season == season)
    if max_rank:
        query = query.filter(DbRanking.rank <= max_rank)
    if as_of_date:
        query = query.filter(DbRanking.as_of_date == as_of_date)
    
    # Order by rank (best first)
    query = query.order_by(DbRanking.rank)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{ranking_id}", response_model=RankingResponse)
def get_ranking(ranking_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific ranking by ID.
    
    Args:
        ranking_id: ID of the ranking
        db: Database session
        
    Returns:
        RankingResponse: Ranking data
        
    Raises:
        HTTPException: If ranking not found
    """
    ranking = db.query(DbRanking).filter(DbRanking.id == ranking_id).first()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")
    return ranking


@router.post("", response_model=RankingResponse, status_code=201)
def create_ranking(ranking: RankingCreate, db: Session = Depends(get_db_session)):
    """
    Create a new ranking.
    
    Args:
        ranking: Ranking data
        db: Database session
        
    Returns:
        RankingResponse: Created ranking data
    """
    db_ranking = DbRanking(
        swimmer_id=ranking.swimmer_id,
        event_id=ranking.event_id,
        time_id=ranking.time_id,
        rank=ranking.rank,
        time_seconds=ranking.time_seconds,
        rank_scope=ranking.rank_scope,
        rank_scope_value=ranking.rank_scope_value,
        season=ranking.season,
        as_of_date=ranking.as_of_date,
        source=ranking.source,
        source_id=ranking.source_id
    )
    db.add(db_ranking)
    db.commit()
    db.refresh(db_ranking)
    return db_ranking


@router.put("/{ranking_id}", response_model=RankingResponse)
def update_ranking(
    ranking_id: int,
    ranking: RankingUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update a ranking.
    
    Args:
        ranking_id: ID of the ranking to update
        ranking: Updated ranking data
        db: Database session
        
    Returns:
        RankingResponse: Updated ranking data
        
    Raises:
        HTTPException: If ranking not found
    """
    db_ranking = db.query(DbRanking).filter(DbRanking.id == ranking_id).first()
    if not db_ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")
    
    # Update fields if provided
    update_data = ranking.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ranking, key, value)
    
    db.commit()
    db.refresh(db_ranking)
    return db_ranking


@router.delete("/{ranking_id}", status_code=204)
def delete_ranking(ranking_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a ranking.
    
    Args:
        ranking_id: ID of the ranking to delete
        db: Database session
        
    Raises:
        HTTPException: If ranking not found
    """
    db_ranking = db.query(DbRanking).filter(DbRanking.id == ranking_id).first()
    if not db_ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")
    
    db.delete(db_ranking)
    db.commit()
    return None


@router.get("/leaderboard/{event_id}", response_model=List[RankingResponse])
def get_leaderboard(
    event_id: int,
    scope: str = "national",
    scope_value: Optional[str] = None,
    season: Optional[str] = None,
    limit: int = 25,
    gender: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a leaderboard for a specific event.
    
    Args:
        event_id: ID of the event
        scope: Ranking scope (e.g., 'national', 'state')
        scope_value: Ranking scope value (e.g., state code)
        season: Filter by season
        limit: Maximum number of records to return
        gender: Filter by gender
        min_age: Filter by minimum age
        max_age: Filter by maximum age
        db: Database session
        
    Returns:
        List[RankingResponse]: Leaderboard rankings
    """
    from sqlalchemy import func
    from database.models import Swimmer
    
    # Build the query
    query = (
        db.query(DbRanking)
        .filter(DbRanking.event_id == event_id)
        .filter(DbRanking.rank_scope == scope)
    )
    
    # Apply filters
    if scope_value:
        query = query.filter(DbRanking.rank_scope_value == scope_value)
    if season:
        query = query.filter(DbRanking.season == season)
    
    # Apply swimmer filters
    if gender or min_age is not None or max_age is not None:
        query = query.join(Swimmer)
        
        if gender:
            query = query.filter(Swimmer.gender == gender)
        if min_age is not None:
            query = query.filter(Swimmer.current_age >= min_age)
        if max_age is not None:
            query = query.filter(Swimmer.current_age <= max_age)
    
    # Get the most recent rankings date
    subquery = (
        db.query(func.max(DbRanking.as_of_date).label('max_date'))
        .filter(DbRanking.event_id == event_id)
        .filter(DbRanking.rank_scope == scope)
    )
    if scope_value:
        subquery = subquery.filter(DbRanking.rank_scope_value == scope_value)
    if season:
        subquery = subquery.filter(DbRanking.season == season)
    
    max_date = subquery.scalar()
    
    if max_date:
        query = query.filter(DbRanking.as_of_date == max_date)
    
    # Order by rank and limit results
    query = query.order_by(DbRanking.rank).limit(limit)
    
    return query.all()
