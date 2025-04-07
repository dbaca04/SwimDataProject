"""
FastAPI application for the Swim Data Project.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from database.database import Database
from config.settings import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Initialize configuration
config = get_config()

# Initialize FastAPI app
app = FastAPI(
    title=config['APP']['name'],
    description=config['APP']['description'],
    version=config['APP']['version']
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config['API']['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database(config['DATABASE'])

# Dependency to get database connection
def get_db():
    return db

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": config['APP']['name'],
        "version": config['APP']['version'],
        "description": config['APP']['description']
    }

@app.get("/swimmers/{swimmer_id}")
def get_swimmer(swimmer_id: int, db: Database = Depends(get_db)):
    """Get a swimmer by ID"""
    swimmer = db.get_swimmer(swimmer_id)
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    return swimmer

@app.get("/swimmers/{swimmer_id}/times")
def get_swimmer_times(
    swimmer_id: int, 
    limit: int = Query(20, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """Get times for a swimmer"""
    swimmer = db.get_swimmer(swimmer_id)
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    times = db.get_swimmer_times(swimmer_id, limit)
    return {
        "swimmer_id": swimmer_id,
        "swimmer_name": swimmer['primary_name'],
        "times": times,
        "count": len(times)
    }

@app.get("/swimmers/{swimmer_id}/best-times")
def get_swimmer_best_times(swimmer_id: int, db: Database = Depends(get_db)):
    """Get best times for a swimmer by event"""
    swimmer = db.get_swimmer(swimmer_id)
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    best_times = db.get_swimmer_best_times(swimmer_id)
    return {
        "swimmer_id": swimmer_id,
        "swimmer_name": swimmer['primary_name'],
        "best_times": best_times,
        "count": len(best_times)
    }

@app.get("/swimmers/{swimmer_id}/rankings")
def get_swimmer_rankings(
    swimmer_id: int, 
    limit: int = Query(20, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """Get rankings for a swimmer"""
    swimmer = db.get_swimmer(swimmer_id)
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    rankings = db.get_swimmer_rankings(swimmer_id, limit)
    return {
        "swimmer_id": swimmer_id,
        "swimmer_name": swimmer['primary_name'],
        "rankings": rankings,
        "count": len(rankings)
    }

@app.get("/events")
def get_events(db: Database = Depends(get_db)):
    """Get all events"""
    events = db.get_events()
    return {
        "events": events,
        "count": len(events)
    }

@app.get("/events/{event_id}/rankings")
def get_event_rankings(
    event_id: int, 
    scope: str = Query("national", description="Ranking scope (national, state, age_group)"),
    scope_value: Optional[str] = Query(None, description="Value for the scope (e.g., state code)"),
    gender: Optional[str] = Query(None, description="Filter by gender (M, F)"),
    age_group: Optional[str] = Query(None, description="Filter by age group"),
    season: Optional[str] = Query(None, description="Filter by season"),
    limit: int = Query(50, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """Get rankings for an event"""
    event = db.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    rankings = db.get_rankings_by_event(
        event_id=event_id,
        rank_scope=scope,
        rank_scope_value=scope_value,
        gender=gender,
        age_group=age_group,
        season=season,
        limit=limit
    )
    
    return {
        "event_id": event_id,
        "event_name": event['name'],
        "scope": scope,
        "scope_value": scope_value,
        "gender": gender,
        "age_group": age_group,
        "season": season,
        "rankings": rankings,
        "count": len(rankings)
    }

@app.get("/compare/swimmers")
def compare_swimmers(
    swimmer_ids: List[int] = Query(..., description="List of swimmer IDs to compare"),
    event_id: Optional[int] = Query(None, description="Filter by event"),
    db: Database = Depends(get_db)
):
    """Compare multiple swimmers"""
    if len(swimmer_ids) < 2 or len(swimmer_ids) > 5:
        raise HTTPException(status_code=400, detail="Must compare between 2 and 5 swimmers")
    
    comparison = {
        "swimmers": [],
        "events": {}
    }
    
    # Get swimmer details
    for swimmer_id in swimmer_ids:
        swimmer = db.get_swimmer(swimmer_id)
        if not swimmer:
            raise HTTPException(status_code=404, detail=f"Swimmer {swimmer_id} not found")
        
        comparison["swimmers"].append({
            "id": swimmer['id'],
            "name": swimmer['primary_name'],
            "gender": swimmer['gender'],
            "state": swimmer['state']
        })
    
    # Get best times for each swimmer
    for swimmer_id in swimmer_ids:
        best_times = db.get_swimmer_best_times(swimmer_id)
        
        # Filter by event if specified
        if event_id is not None:
            best_times = [t for t in best_times if t['event_id'] == event_id]
        
        # Add to comparison
        for time in best_times:
            event_id = time['event_id']
            event_name = time['event_name']
            
            # Add event to comparison if not exists
            if event_id not in comparison["events"]:
                comparison["events"][event_id] = {
                    "id": event_id,
                    "name": event_name,
                    "times": {}
                }
            
            # Add time to event
            comparison["events"][event_id]["times"][swimmer_id] = {
                "time_seconds": time['best_time_seconds'],
                "time_formatted": time['time_formatted'],
                "date": time['time_date'],
                "meet_name": time['meet_name']
            }
    
    # Convert events dict to list
    comparison["events"] = list(comparison["events"].values())
    
    return comparison

def start():
    """Start the API server"""
    import uvicorn
    
    # Get API settings
    api_config = config['API']
    
    # Start server
    uvicorn.run(
        "api.app:app",
        host=api_config['host'],
        port=api_config['port'],
        reload=api_config['debug'],
        log_level=api_config['log_level']
    )

if __name__ == "__main__":
    start()
