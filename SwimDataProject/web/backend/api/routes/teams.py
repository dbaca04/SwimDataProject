"""
Teams Routes

This module contains API routes for team/school data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from database.database import get_db_session
from database.models import Team as DbTeam
from web.backend.api.models import TeamResponse, TeamCreate, TeamUpdate

router = APIRouter()


@router.get("", response_model=List[TeamResponse])
def get_teams(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    type: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of teams with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        name: Filter by name (partial match)
        type: Filter by team type
        state: Filter by state
        country: Filter by country
        active: Filter by active status
        db: Database session
        
    Returns:
        List[TeamResponse]: List of teams
    """
    query = db.query(DbTeam)
    
    # Apply filters
    if name:
        query = query.filter(DbTeam.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(DbTeam.type == type)
    if state:
        query = query.filter(DbTeam.state == state)
    if country:
        query = query.filter(DbTeam.country == country)
    if active is not None:
        query = query.filter(DbTeam.active == active)
    
    # Order by name
    query = query.order_by(DbTeam.name)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific team by ID.
    
    Args:
        team_id: ID of the team
        db: Database session
        
    Returns:
        TeamResponse: Team data
        
    Raises:
        HTTPException: If team not found
    """
    team = db.query(DbTeam).filter(DbTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("", response_model=TeamResponse, status_code=201)
def create_team(team: TeamCreate, db: Session = Depends(get_db_session)):
    """
    Create a new team.
    
    Args:
        team: Team data
        db: Database session
        
    Returns:
        TeamResponse: Created team data
    """
    db_team = DbTeam(
        name=team.name,
        short_name=team.short_name,
        type=team.type,
        state=team.state,
        country=team.country
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team: TeamUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update a team.
    
    Args:
        team_id: ID of the team to update
        team: Updated team data
        db: Database session
        
    Returns:
        TeamResponse: Updated team data
        
    Raises:
        HTTPException: If team not found
    """
    db_team = db.query(DbTeam).filter(DbTeam.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Update fields if provided
    update_data = team.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_team, key, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a team.
    
    Args:
        team_id: ID of the team to delete
        db: Database session
        
    Raises:
        HTTPException: If team not found
    """
    db_team = db.query(DbTeam).filter(DbTeam.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db.delete(db_team)
    db.commit()
    return None


@router.get("/by-name/{name}", response_model=List[TeamResponse])
def get_teams_by_name(name: str, db: Session = Depends(get_db_session)):
    """
    Get teams by name (exact or partial match).
    
    Args:
        name: Team name to search for
        db: Database session
        
    Returns:
        List[TeamResponse]: List of teams matching the name
    """
    teams = db.query(DbTeam).filter(DbTeam.name.ilike(f"%{name}%")).all()
    return teams


@router.get("/alias/{alias_name}", response_model=List[TeamResponse])
def get_teams_by_alias(alias_name: str, db: Session = Depends(get_db_session)):
    """
    Get teams by an alias name.
    
    Args:
        alias_name: Alias name to look up
        db: Database session
        
    Returns:
        List[TeamResponse]: Teams corresponding to the alias
    """
    from database.models import TeamAlias
    
    # Look up the teams through aliases
    aliases = db.query(TeamAlias).filter(TeamAlias.name_alias.ilike(f"%{alias_name}%")).all()
    if not aliases:
        return []
    
    # Get the team IDs
    team_ids = [alias.team_id for alias in aliases]
    
    # Get the teams
    teams = db.query(DbTeam).filter(DbTeam.id.in_(team_ids)).all()
    return teams


@router.get("/by-type/{type}", response_model=List[TeamResponse])
def get_teams_by_type(
    type: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get teams by type (e.g., 'high_school', 'club').
    
    Args:
        type: Team type to filter by
        state: Optional state filter
        db: Database session
        
    Returns:
        List[TeamResponse]: List of teams of the specified type
    """
    query = db.query(DbTeam).filter(DbTeam.type == type)
    
    if state:
        query = query.filter(DbTeam.state == state)
    
    return query.order_by(DbTeam.name).all()


@router.get("/swimmers/{team_id}", response_model=List[int])
def get_team_swimmers(
    team_id: int,
    is_current: bool = True,
    db: Session = Depends(get_db_session)
):
    """
    Get IDs of swimmers affiliated with a team.
    
    Args:
        team_id: ID of the team
        is_current: Filter by current affiliation status
        db: Database session
        
    Returns:
        List[int]: List of swimmer IDs
        
    Raises:
        HTTPException: If team not found
    """
    from database.models import SwimmerTeamAffiliation
    
    # Check if team exists
    team = db.query(DbTeam).filter(DbTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Query affiliations
    query = (
        db.query(SwimmerTeamAffiliation.swimmer_id)
        .filter(SwimmerTeamAffiliation.team_id == team_id)
    )
    
    if is_current:
        query = query.filter(SwimmerTeamAffiliation.is_current == True)
    
    swimmer_ids = [row[0] for row in query.all()]
    return swimmer_ids
