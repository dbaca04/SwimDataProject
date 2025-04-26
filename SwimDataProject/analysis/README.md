# Analytics Module

This module provides advanced analytics and visualization capabilities for swimming data.

## Overview

The analytics module contains functions for analyzing swimming performance data and generating visualizations. It enables users to:

1. **Track Swimmer Progression**: Analyze how a swimmer's times have improved over time in specific events
2. **Compare With Standards**: Compare swimmer's times against qualifying standards (like state cuts, national cuts, etc.)
3. **Compare With Elite Times**: Compare high school swimmers with elite and Olympic level times
4. **Analyze Peer Groups**: Calculate statistics for peer groups based on age, gender, and location
5. **Calculate Rankings**: Determine a swimmer's ranking at various levels (national, state, age group)
6. **Generate Visualizations**: Create charts and graphs visualizing performance data

## Components

The module consists of two main components:

### `swimmer_analysis.py`

Contains analysis functions that process data and generate metrics:

- `calculate_progression`: Calculates a swimmer's time progression in an event
- `compare_with_standards`: Compares times with qualification standards
- `compare_with_elite`: Compares with elite/Olympic times
- `get_peer_statistics`: Calculates statistics for peer groups
- `calculate_rankings`: Determines rankings at different levels

### `visualization.py`

Contains functions to generate visualizations based on the analysis:

- `create_progression_chart`: Time progression chart
- `create_standards_comparison_chart`: Comparison with time standards
- `create_percentile_chart`: Percentile ranking visualization
- `create_peer_distribution_chart`: Distribution of times within peer group
- `create_elite_comparison_chart`: Comparison with elite swimmers

## Usage

### Basic Analysis

```python
from database.database import SessionLocal
from analysis.swimmer_analysis import calculate_progression

# Create database session
db_session = SessionLocal()

try:
    # Get progression data for a swimmer in an event
    progression_data = calculate_progression(
        swimmer_id=123,  # Replace with actual swimmer ID
        event_id=456,    # Replace with actual event ID
        db_session=db_session
    )
    
    print(f"Total improvement: {progression_data['total_improvement']} seconds")
    print(f"Yearly improvement rate: {progression_data['avg_improvement_per_year']} sec/year")
    
    # Get personal best
    if progression_data["has_data"] and progression_data["times"]:
        best_time = min(progression_data["times"], key=lambda x: x["time_seconds"])
        print(f"Personal best: {best_time['time_formatted']}")
finally:
    db_session.close()
```

### Creating Visualizations

```python
from database.database import SessionLocal
from analysis.visualization import create_progression_chart

# Create database session
db_session = SessionLocal()

try:
    # Generate a progression chart
    chart_data = create_progression_chart(
        swimmer_id=123,  # Replace with actual swimmer ID
        event_id=456,    # Replace with actual event ID
        db_session=db_session
    )
    
    # The chart_data is a base64 encoded PNG image
    # You can display it in a web page like this:
    html = f'<img src="data:image/png;base64,{chart_data}" alt="Progression Chart">'
    
    # Or save it to a file
    import base64
    with open("progression_chart.png", "wb") as f:
        f.write(base64.b64decode(chart_data))
finally:
    db_session.close()
```

### Using the Web API

The analytics functions are also available through the API:

- `GET /api/analytics/swimmer/{swimmer_id}/progression/{event_id}`: Get progression data
- `GET /api/analytics/swimmer/{swimmer_id}/standards/{event_id}`: Get standards comparison
- `GET /api/analytics/swimmer/{swimmer_id}/elite/{event_id}`: Get elite comparison
- `GET /api/analytics/swimmer/{swimmer_id}/rankings/{event_id}`: Get rankings
- `GET /api/analytics/peer-statistics/{event_id}`: Get peer statistics

Visualization endpoints:

- `GET /api/analytics/visualize/progression/{swimmer_id}/{event_id}`: Get progression chart
- `GET /api/analytics/visualize/standards/{swimmer_id}/{event_id}`: Get standards comparison chart
- `GET /api/analytics/visualize/percentile/{swimmer_id}/{event_id}`: Get percentile chart
- `GET /api/analytics/visualize/peer-distribution/{event_id}`: Get peer distribution chart
- `GET /api/analytics/visualize/elite/{swimmer_id}/{event_id}`: Get elite comparison chart

## Demo Script

For a demonstration of the analytics capabilities, see `demo_analytics.py` in the project root. This script creates sample data and demonstrates all the analytics and visualization functions.

To run the demo:

```bash
# Reset the database and run all demos
python demo_analytics.py --reset-db --demo all

# Run a specific demo
python demo_analytics.py --demo progression

# Available demos: progression, standards, elite, peers, rankings
```

The demo script will create chart files in a `chart_output` directory.

## Dependencies

The analytics module depends on the following packages:
- pandas
- numpy
- matplotlib
- seaborn

Make sure these are installed in your environment.
