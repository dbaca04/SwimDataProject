"""
API routes for analytics and visualizations.

This module provides endpoints for accessing swimming data analytics and visualizations.
"""
import os
import sys
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any

# Add the parent directory to the path to allow importing project modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.database import get_db
from database.models import Swimmer, Event, SwimTime

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

# Create router
router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/swimmer/{swimmer_id}/progression/{event_id}")
async def get_swimmer_progression(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get swimmer's time progression for a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Progression data with dates, times, and improvement metrics
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Get progression data
        progression_data = calculate_progression(swimmer_id, event_id, db)
        
        return progression_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swimmer progression: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting swimmer progression: {str(e)}")


@router.get("/swimmer/{swimmer_id}/standards/{event_id}")
async def get_swimmer_standards_comparison(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get comparison of swimmer's times with time standards.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Comparison with time standards
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Get standards comparison data
        comparison_data = compare_with_standards(swimmer_id, event_id, db)
        
        return comparison_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting standards comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting standards comparison: {str(e)}")


@router.get("/swimmer/{swimmer_id}/elite/{event_id}")
async def get_swimmer_elite_comparison(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get comparison of swimmer's times with elite/Olympic times.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Comparison with elite swimmers
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Get elite comparison data
        comparison_data = compare_with_elite(swimmer_id, event_id, db)
        
        return comparison_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting elite comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting elite comparison: {str(e)}")


@router.get("/swimmer/{swimmer_id}/rankings/{event_id}")
async def get_swimmer_rankings(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get rankings for a swimmer in a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Ranking data
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Get rankings data
        rankings_data = calculate_rankings(swimmer_id, event_id, db)
        
        return rankings_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swimmer rankings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting swimmer rankings: {str(e)}")


@router.get("/peer-statistics/{event_id}")
async def get_peer_group_statistics(
    event_id: int,
    gender: str,
    age_min: int,
    age_max: int,
    state: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get statistics for a peer group in a specific event.
    
    Args:
        event_id: Event ID
        gender: Gender ('M' or 'F')
        age_min: Minimum age for peer group
        age_max: Maximum age for peer group
        state: State code to filter by (e.g., 'CA')
        
    Returns:
        Peer group statistics
    """
    try:
        # Check if event exists
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Validate gender
        if gender not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="Gender must be 'M' or 'F'")
        
        # Validate age range
        if age_min < 0 or age_max < age_min:
            raise HTTPException(status_code=400, detail="Invalid age range")
        
        # Get peer statistics
        stats_data = get_peer_statistics(event_id, gender, age_min, age_max, state, db)
        
        return stats_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting peer statistics: {str(e)}")


# Visualization endpoints

@router.get("/visualize/progression/{swimmer_id}/{event_id}")
async def get_progression_chart(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get a progression chart for a swimmer in a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Create chart
        chart_data = create_progression_chart(swimmer_id, event_id, db)
        
        return {"chart": chart_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating progression chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating progression chart: {str(e)}")


@router.get("/visualize/standards/{swimmer_id}/{event_id}")
async def get_standards_comparison_chart(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get a standards comparison chart for a swimmer in a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Create chart
        chart_data = create_standards_comparison_chart(swimmer_id, event_id, db)
        
        return {"chart": chart_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating standards comparison chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating standards comparison chart: {str(e)}")


@router.get("/visualize/percentile/{swimmer_id}/{event_id}")
async def get_percentile_chart(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get a percentile chart for a swimmer in a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Create chart
        chart_data = create_percentile_chart(swimmer_id, event_id, db)
        
        return {"chart": chart_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating percentile chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating percentile chart: {str(e)}")


@router.get("/visualize/peer-distribution/{event_id}")
async def get_peer_distribution_chart(
    event_id: int,
    gender: str,
    age_min: int,
    age_max: int,
    state: Optional[str] = None,
    swimmer_id: Optional[int] = None,
    db = Depends(get_db)
):
    """
    Get a peer distribution chart for a specific event.
    
    Args:
        event_id: Event ID
        gender: Gender ('M' or 'F')
        age_min: Minimum age for peer group
        age_max: Maximum age for peer group
        state: State code to filter by (e.g., 'CA')
        swimmer_id: Optional swimmer ID to highlight in the distribution
        
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Check if event exists
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Validate gender
        if gender not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="Gender must be 'M' or 'F'")
        
        # Validate age range
        if age_min < 0 or age_max < age_min:
            raise HTTPException(status_code=400, detail="Invalid age range")
        
        # Get swimmer's best time if swimmer_id is provided
        swimmer_time = None
        if swimmer_id is not None:
            # Check if swimmer exists
            swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
            
            if not swimmer:
                raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
            
            # Get best time
            best_time = db.query(SwimTime).filter(
                SwimTime.swimmer_id == swimmer_id,
                SwimTime.event_id == event_id
            ).order_by(SwimTime.time_seconds).first()
            
            if best_time:
                swimmer_time = best_time.time_seconds
        
        # Create chart
        chart_data = create_peer_distribution_chart(event_id, gender, age_min, age_max, state, swimmer_time, db)
        
        return {"chart": chart_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating peer distribution chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating peer distribution chart: {str(e)}")


@router.get("/visualize/elite/{swimmer_id}/{event_id}")
async def get_elite_comparison_chart(
    swimmer_id: int,
    event_id: int,
    db = Depends(get_db)
):
    """
    Get an elite comparison chart for a swimmer in a specific event.
    
    Args:
        swimmer_id: Swimmer ID
        event_id: Event ID
        
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Check if swimmer and event exist
        swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer with ID {swimmer_id} not found")
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Create chart
        chart_data = create_elite_comparison_chart(swimmer_id, event_id, db)
        
        return {"chart": chart_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating elite comparison chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating elite comparison chart: {str(e)}")
