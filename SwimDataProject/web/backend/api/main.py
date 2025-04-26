"""
Main API router for the Swim Data Project.

This module registers all API route modules and creates the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import route modules
from .routes import swimmers, teams, events, times, rankings, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Create FastAPI app
app = FastAPI(
    title="Swim Data API",
    description="API for accessing swimming data",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (modify for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(swimmers.router)
app.include_router(teams.router)
app.include_router(events.router)
app.include_router(times.router)
app.include_router(rankings.router)
app.include_router(analytics.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Swim Data API",
        "version": "0.1.0",
        "documentation": "/docs",
    }
