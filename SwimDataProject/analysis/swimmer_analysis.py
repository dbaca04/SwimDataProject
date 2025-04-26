"""
Swimmer analysis module.

This module provides functions for analyzing swimmer performance data.
"""
import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.models import Swimmer, Event, SwimTime, Ranking, TimeStandard, Record


# Configure logging
logger = logging.getLogger(__name__)


def calculate_progression(swimmer_id, event_id, db_session):
    """
    Calculate swimmer's time progression for a specific event.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        dict: Progression data with dates, times, and improvement metrics
    """
    try:
        # Query all times for this swimmer in this event, ordered by date
        times = db_session.query(SwimTime).filter(
            SwimTime.swimmer_id == swimmer_id,
            SwimTime.event_id == event_id
        ).order_by(SwimTime.date).all()
        
        if not times:
            logger.info(f"No times found for swimmer {swimmer_id} in event {event_id}")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "times": [],
                "total_improvement": 0,
                "avg_improvement_per_year": 0,
                "has_data": False
            }
        
        # Get event and swimmer details
        event = db_session.query(Event).filter(Event.id == event_id).first()
        swimmer = db_session.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        
        # Calculate improvement between times
        time_data = []
        prev_time = None
        
        for i, time_obj in enumerate(times):
            time_info = {
                "date": time_obj.date,
                "time_seconds": time_obj.time_seconds,
                "time_formatted": time_obj.time_formatted,
                "meet_name": time_obj.meet_name if hasattr(time_obj, 'meet_name') else None,
                "age": time_obj.swimmer_age,
                "improvement": 0,  # Default value
                "improvement_percent": 0  # Default value
            }
            
            # Calculate improvement from previous time
            if prev_time is not None:
                improvement = prev_time["time_seconds"] - time_info["time_seconds"]
                improvement_percent = (improvement / prev_time["time_seconds"]) * 100
                time_info["improvement"] = round(improvement, 2)
                time_info["improvement_percent"] = round(improvement_percent, 2)
            
            time_data.append(time_info)
            prev_time = time_info
        
        # Calculate overall improvement
        if len(time_data) >= 2:
            first_time = time_data[0]["time_seconds"]
            last_time = time_data[-1]["time_seconds"]
            total_improvement = first_time - last_time
            total_improvement_percent = (total_improvement / first_time) * 100
            
            # Calculate time span in years
            first_date = time_data[0]["date"]
            last_date = time_data[-1]["date"]
            time_span_days = (last_date - first_date).days
            time_span_years = time_span_days / 365.25
            
            # Average improvement per year
            if time_span_years > 0:
                avg_improvement_per_year = total_improvement / time_span_years
                avg_improvement_percent_per_year = total_improvement_percent / time_span_years
            else:
                avg_improvement_per_year = 0
                avg_improvement_percent_per_year = 0
        else:
            total_improvement = 0
            total_improvement_percent = 0
            avg_improvement_per_year = 0
            avg_improvement_percent_per_year = 0
            time_span_days = 0
            time_span_years = 0
        
        # Build response
        result = {
            "swimmer_id": swimmer_id,
            "swimmer_name": swimmer.primary_name if swimmer else "Unknown",
            "event_id": event_id,
            "event_name": event.name if event else "Unknown",
            "course": event.course if event else "Unknown",
            "times": time_data,
            "total_improvement": round(total_improvement, 2),
            "total_improvement_percent": round(total_improvement_percent, 2),
            "time_span_days": time_span_days,
            "time_span_years": round(time_span_years, 2),
            "avg_improvement_per_year": round(avg_improvement_per_year, 2),
            "avg_improvement_percent_per_year": round(avg_improvement_percent_per_year, 2),
            "has_data": True,
            "personal_best": time_data[-1] if time_data else None
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating progression: {str(e)}")
        return {
            "swimmer_id": swimmer_id,
            "event_id": event_id,
            "error": str(e),
            "has_data": False
        }


def compare_with_standards(swimmer_id, event_id, db_session):
    """
    Compare swimmer's times with time standards.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        dict: Comparison with time standards
    """
    try:
        # Get swimmer and event details
        swimmer = db_session.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db_session.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer or not event:
            logger.warning(f"Swimmer {swimmer_id} or event {event_id} not found")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Get swimmer's personal best
        best_time = db_session.query(SwimTime).filter(
            SwimTime.swimmer_id == swimmer_id,
            SwimTime.event_id == event_id
        ).order_by(SwimTime.time_seconds).first()
        
        if not best_time:
            logger.info(f"No times found for swimmer {swimmer_id} in event {event_id}")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Get relevant time standards for this swimmer and event
        gender = swimmer.gender
        age = swimmer.current_age or 0
        
        # Find age group
        age_groups = ["11-12", "13-14", "15-16", "17-18", "Open"]
        swimmer_age_group = "Open"  # Default
        
        for age_group in age_groups:
            min_age, max_age = map(int, age_group.split('-')) if '-' in age_group else (0, 100)
            if min_age <= age <= max_age:
                swimmer_age_group = age_group
                break
        
        # Query time standards
        standards = db_session.query(TimeStandard).filter(
            TimeStandard.event_id == event_id,
            TimeStandard.gender == gender
        ).order_by(TimeStandard.time_seconds).all()
        
        # Get age-specific standards
        age_standards = [s for s in standards if s.age_group == swimmer_age_group]
        
        # If no age-specific standards, use Open if available
        if not age_standards:
            age_standards = [s for s in standards if s.age_group == "Open"]
        
        # Compare with standards
        comparisons = []
        
        for standard in age_standards:
            time_diff = best_time.time_seconds - standard.time_seconds
            percent_diff = (time_diff / standard.time_seconds) * 100
            
            comparison = {
                "standard_name": standard.standard_name,
                "standard_time_seconds": standard.time_seconds,
                "standard_time_formatted": standard.time_formatted,
                "time_difference": round(time_diff, 2),
                "percent_difference": round(percent_diff, 2),
                "achieves_standard": best_time.time_seconds <= standard.time_seconds
            }
            
            comparisons.append(comparison)
        
        # Build response
        result = {
            "swimmer_id": swimmer_id,
            "swimmer_name": swimmer.primary_name,
            "gender": gender,
            "age": age,
            "age_group": swimmer_age_group,
            "event_id": event_id,
            "event_name": event.name,
            "course": event.course,
            "best_time_seconds": best_time.time_seconds,
            "best_time_formatted": best_time.time_formatted,
            "comparisons": comparisons,
            "standards_count": len(comparisons),
            "has_data": True
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error comparing with standards: {str(e)}")
        return {
            "swimmer_id": swimmer_id,
            "event_id": event_id,
            "error": str(e),
            "has_data": False
        }


def compare_with_elite(swimmer_id, event_id, db_session):
    """
    Compare high school swimmer with elite/Olympic level times.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        dict: Comparison with elite swimmers
    """
    try:
        # Get swimmer and event details
        swimmer = db_session.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db_session.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer or not event:
            logger.warning(f"Swimmer {swimmer_id} or event {event_id} not found")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Get swimmer's personal best
        best_time = db_session.query(SwimTime).filter(
            SwimTime.swimmer_id == swimmer_id,
            SwimTime.event_id == event_id
        ).order_by(SwimTime.time_seconds).first()
        
        if not best_time:
            logger.info(f"No times found for swimmer {swimmer_id} in event {event_id}")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Get records for this event
        gender = swimmer.gender
        
        # National records
        national_record = db_session.query(Record).filter(
            Record.event_id == event_id,
            Record.gender == gender,
            Record.record_type == 'national_high_school',
            Record.is_current == True
        ).first()
        
        # State records
        state_record = None
        if swimmer.state:
            state_record = db_session.query(Record).filter(
                Record.event_id == event_id,
                Record.gender == gender,
                Record.record_type == 'state_high_school',
                Record.scope == swimmer.state,
                Record.is_current == True
            ).first()
        
        # Get Olympic standard (if available)
        olympic_standard = db_session.query(TimeStandard).filter(
            TimeStandard.event_id == event_id,
            TimeStandard.gender == gender,
            TimeStandard.standard_name.like('%Olympic%')
        ).order_by(TimeStandard.time_seconds).first()
        
        # Get Olympic Trials cut (if available)
        trials_cut = db_session.query(TimeStandard).filter(
            TimeStandard.event_id == event_id,
            TimeStandard.gender == gender,
            TimeStandard.standard_name.like('%Trials%')
        ).order_by(TimeStandard.time_seconds).first()
        
        # Define comparison benchmarks
        comparisons = []
        
        # National high school record
        if national_record:
            time_diff = best_time.time_seconds - national_record.time_seconds
            percent_diff = (time_diff / national_record.time_seconds) * 100
            
            comparisons.append({
                "benchmark_name": "National High School Record",
                "benchmark_time_seconds": national_record.time_seconds,
                "benchmark_time_formatted": national_record.time_formatted,
                "holder_name": national_record.swimmer_name,
                "holder_school": national_record.team_name,
                "record_year": national_record.record_date.year if national_record.record_date else None,
                "time_difference": round(time_diff, 2),
                "percent_difference": round(percent_diff, 2),
                "achieves_benchmark": best_time.time_seconds <= national_record.time_seconds
            })
        
        # State high school record
        if state_record:
            time_diff = best_time.time_seconds - state_record.time_seconds
            percent_diff = (time_diff / state_record.time_seconds) * 100
            
            comparisons.append({
                "benchmark_name": f"{swimmer.state} State High School Record",
                "benchmark_time_seconds": state_record.time_seconds,
                "benchmark_time_formatted": state_record.time_formatted,
                "holder_name": state_record.swimmer_name,
                "holder_school": state_record.team_name,
                "record_year": state_record.record_date.year if state_record.record_date else None,
                "time_difference": round(time_diff, 2),
                "percent_difference": round(percent_diff, 2),
                "achieves_benchmark": best_time.time_seconds <= state_record.time_seconds
            })
        
        # Olympic standard
        if olympic_standard:
            time_diff = best_time.time_seconds - olympic_standard.time_seconds
            percent_diff = (time_diff / olympic_standard.time_seconds) * 100
            
            comparisons.append({
                "benchmark_name": "Olympic Standard",
                "benchmark_time_seconds": olympic_standard.time_seconds,
                "benchmark_time_formatted": olympic_standard.time_formatted,
                "time_difference": round(time_diff, 2),
                "percent_difference": round(percent_diff, 2),
                "achieves_benchmark": best_time.time_seconds <= olympic_standard.time_seconds
            })
        
        # Olympic Trials cut
        if trials_cut:
            time_diff = best_time.time_seconds - trials_cut.time_seconds
            percent_diff = (time_diff / trials_cut.time_seconds) * 100
            
            comparisons.append({
                "benchmark_name": "Olympic Trials Cut",
                "benchmark_time_seconds": trials_cut.time_seconds,
                "benchmark_time_formatted": trials_cut.time_formatted,
                "time_difference": round(time_diff, 2),
                "percent_difference": round(percent_diff, 2),
                "achieves_benchmark": best_time.time_seconds <= trials_cut.time_seconds
            })
        
        # Calculate pathway metrics
        pathway_metrics = {}
        
        if trials_cut and best_time:
            # Time needed to improve to reach Trials cut
            time_to_trials = best_time.time_seconds - trials_cut.time_seconds
            
            # If using average improvement rate, how long would it take to reach Trials cut
            avg_improvement = calculate_progression(swimmer_id, event_id, db_session)
            if avg_improvement.get("has_data") and avg_improvement.get("avg_improvement_per_year") > 0:
                years_to_trials = abs(time_to_trials / avg_improvement["avg_improvement_per_year"])
                pathway_metrics["years_to_trials_cut"] = round(years_to_trials, 1)
            
            # Improvement percentage needed
            if best_time.time_seconds > 0:
                percent_improvement_needed = (time_to_trials / best_time.time_seconds) * 100
                pathway_metrics["percent_improvement_needed"] = round(percent_improvement_needed, 2)
        
        # Build response
        result = {
            "swimmer_id": swimmer_id,
            "swimmer_name": swimmer.primary_name,
            "gender": gender,
            "age": swimmer.current_age,
            "state": swimmer.state,
            "event_id": event_id,
            "event_name": event.name,
            "course": event.course,
            "best_time_seconds": best_time.time_seconds,
            "best_time_formatted": best_time.time_formatted,
            "comparisons": comparisons,
            "pathway_metrics": pathway_metrics,
            "has_data": True
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error comparing with elite: {str(e)}")
        return {
            "swimmer_id": swimmer_id,
            "event_id": event_id,
            "error": str(e),
            "has_data": False
        }


def get_peer_statistics(event_id, gender, age_min, age_max, state=None, db_session=None):
    """
    Get statistics for a peer group in a specific event.
    
    Args:
        event_id (int): Event ID
        gender (str): Gender ('M' or 'F')
        age_min (int): Minimum age for peer group
        age_max (int): Maximum age for peer group
        state (str, optional): State code to filter by (e.g., 'CA')
        db_session: Database session
        
    Returns:
        dict: Peer group statistics
    """
    try:
        # Create base query
        query = db_session.query(SwimTime).join(Swimmer).filter(
            SwimTime.event_id == event_id,
            Swimmer.gender == gender,
            SwimTime.swimmer_age >= age_min,
            SwimTime.swimmer_age <= age_max
        )
        
        # Add state filter if provided
        if state:
            query = query.filter(Swimmer.state == state)
        
        # Get all times
        times = query.all()
        
        if not times:
            logger.info(f"No times found for event {event_id}, gender {gender}, ages {age_min}-{age_max}")
            return {
                "event_id": event_id,
                "gender": gender,
                "age_range": f"{age_min}-{age_max}",
                "state": state,
                "has_data": False
            }
        
        # Get event details
        event = db_session.query(Event).filter(Event.id == event_id).first()
        
        # Extract time values
        time_values = [t.time_seconds for t in times]
        
        # Calculate statistics
        stats = {
            "count": len(time_values),
            "mean": np.mean(time_values),
            "median": np.median(time_values),
            "min": np.min(time_values),
            "max": np.max(time_values),
            "std": np.std(time_values),
            "percentile_10": np.percentile(time_values, 10),
            "percentile_25": np.percentile(time_values, 25),
            "percentile_75": np.percentile(time_values, 75),
            "percentile_90": np.percentile(time_values, 90),
            "percentile_95": np.percentile(time_values, 95),
            "percentile_99": np.percentile(time_values, 99)
        }
        
        # Round all statistics
        for key in stats:
            if isinstance(stats[key], (int, float)) and key != "count":
                stats[key] = round(stats[key], 2)
        
        # Build response
        result = {
            "event_id": event_id,
            "event_name": event.name if event else "Unknown",
            "course": event.course if event else "Unknown",
            "gender": gender,
            "age_range": f"{age_min}-{age_max}",
            "state": state,
            "statistics": stats,
            "has_data": True
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting peer statistics: {str(e)}")
        return {
            "event_id": event_id,
            "gender": gender,
            "age_range": f"{age_min}-{age_max}",
            "state": state,
            "error": str(e),
            "has_data": False
        }


def calculate_rankings(swimmer_id, event_id, db_session):
    """
    Calculate rankings for a swimmer in a specific event.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        dict: Ranking data
    """
    try:
        # Get swimmer and event details
        swimmer = db_session.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
        event = db_session.query(Event).filter(Event.id == event_id).first()
        
        if not swimmer or not event:
            logger.warning(f"Swimmer {swimmer_id} or event {event_id} not found")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Get swimmer's personal best
        best_time = db_session.query(SwimTime).filter(
            SwimTime.swimmer_id == swimmer_id,
            SwimTime.event_id == event_id
        ).order_by(SwimTime.time_seconds).first()
        
        if not best_time:
            logger.info(f"No times found for swimmer {swimmer_id} in event {event_id}")
            return {
                "swimmer_id": swimmer_id,
                "event_id": event_id,
                "has_data": False
            }
        
        # Determine age group
        age = swimmer.current_age or best_time.swimmer_age or 0
        gender = swimmer.gender
        
        # Define ranking scopes
        rankings = []
        
        # National ranking
        national_count = db_session.query(SwimTime).join(Swimmer).filter(
            SwimTime.event_id == event_id,
            Swimmer.gender == gender,
            SwimTime.time_seconds < best_time.time_seconds
        ).count()
        
        national_total = db_session.query(SwimTime).join(Swimmer).filter(
            SwimTime.event_id == event_id,
            Swimmer.gender == gender
        ).count()
        
        rankings.append({
            "scope": "National",
            "scope_value": "USA",
            "rank": national_count + 1,
            "total": national_total,
            "percentile": round((1 - (national_count / national_total)) * 100, 2) if national_total > 0 else 0
        })
        
        # State ranking
        if swimmer.state:
            state_count = db_session.query(SwimTime).join(Swimmer).filter(
                SwimTime.event_id == event_id,
                Swimmer.gender == gender,
                Swimmer.state == swimmer.state,
                SwimTime.time_seconds < best_time.time_seconds
            ).count()
            
            state_total = db_session.query(SwimTime).join(Swimmer).filter(
                SwimTime.event_id == event_id,
                Swimmer.gender == gender,
                Swimmer.state == swimmer.state
            ).count()
            
            rankings.append({
                "scope": "State",
                "scope_value": swimmer.state,
                "rank": state_count + 1,
                "total": state_total,
                "percentile": round((1 - (state_count / state_total)) * 100, 2) if state_total > 0 else 0
            })
        
        # Age group ranking (national)
        if age > 0:
            age_min = (age // 2) * 2 - 1  # Round down to odd age (e.g., 15 for 15-16)
            age_max = age_min + 1
            
            age_count = db_session.query(SwimTime).join(Swimmer).filter(
                SwimTime.event_id == event_id,
                Swimmer.gender == gender,
                SwimTime.swimmer_age >= age_min,
                SwimTime.swimmer_age <= age_max,
                SwimTime.time_seconds < best_time.time_seconds
            ).count()
            
            age_total = db_session.query(SwimTime).join(Swimmer).filter(
                SwimTime.event_id == event_id,
                Swimmer.gender == gender,
                SwimTime.swimmer_age >= age_min,
                SwimTime.swimmer_age <= age_max
            ).count()
            
            rankings.append({
                "scope": "Age Group",
                "scope_value": f"{age_min}-{age_max}",
                "rank": age_count + 1,
                "total": age_total,
                "percentile": round((1 - (age_count / age_total)) * 100, 2) if age_total > 0 else 0
            })
            
            # Age group ranking (state)
            if swimmer.state:
                age_state_count = db_session.query(SwimTime).join(Swimmer).filter(
                    SwimTime.event_id == event_id,
                    Swimmer.gender == gender,
                    Swimmer.state == swimmer.state,
                    SwimTime.swimmer_age >= age_min,
                    SwimTime.swimmer_age <= age_max,
                    SwimTime.time_seconds < best_time.time_seconds
                ).count()
                
                age_state_total = db_session.query(SwimTime).join(Swimmer).filter(
                    SwimTime.event_id == event_id,
                    Swimmer.gender == gender,
                    Swimmer.state == swimmer.state,
                    SwimTime.swimmer_age >= age_min,
                    SwimTime.swimmer_age <= age_max
                ).count()
                
                rankings.append({
                    "scope": "State Age Group",
                    "scope_value": f"{swimmer.state} {age_min}-{age_max}",
                    "rank": age_state_count + 1,
                    "total": age_state_total,
                    "percentile": round((1 - (age_state_count / age_state_total)) * 100, 2) if age_state_total > 0 else 0
                })
        
        # Build response
        result = {
            "swimmer_id": swimmer_id,
            "swimmer_name": swimmer.primary_name,
            "gender": gender,
            "age": age,
            "state": swimmer.state,
            "event_id": event_id,
            "event_name": event.name,
            "course": event.course,
            "best_time_seconds": best_time.time_seconds,
            "best_time_formatted": best_time.time_formatted,
            "rankings": rankings,
            "has_data": True
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating rankings: {str(e)}")
        return {
            "swimmer_id": swimmer_id,
            "event_id": event_id,
            "error": str(e),
            "has_data": False
        }
