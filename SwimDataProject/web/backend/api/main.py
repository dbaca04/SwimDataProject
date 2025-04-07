"""
Main API Application

This module defines the FastAPI application and includes all routes.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Import database
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from database.database import get_db_session
from web.backend.api.models import SwimmerResponse, TimeResponse, RankingResponse
from web.backend.api.routes import swimmers, times, rankings, events, teams

# Create FastAPI app
app = FastAPI(
    title="Swimming Data API",
    description="API for accessing swimming data and analytics",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(swimmers.router, prefix="/api/swimmers", tags=["swimmers"])
app.include_router(times.router, prefix="/api/times", tags=["times"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["rankings"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])


@app.get("/")
def read_root():
    """
    Root endpoint returning API information.
    
    Returns:
        dict: API information
    """
    return {
        "name": "Swimming Data API",
        "version": "0.1.0",
        "documentation": "/docs",
    }


@app.get("/api/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
