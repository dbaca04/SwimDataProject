# Swim Data Project

## Project Overview
This project aims to create a comprehensive swimming data platform focused on high school swimmers, allowing them to compare their performance against peers at the city, state, regional, national, and international levels. Our approach relies on web scraping to collect data from various public sources, as we currently don't have partnerships with swimming organizations.

## Table of Contents

1. [Project Planning](./01-project-planning.md)
   - Project goals and scope
   - Target audiences
   - Key features

2. [Data Sources Analysis](./02-data-sources.md)
   - Available public data sources
   - Technical accessibility analysis
   - Data formats and structures

3. [Web Scraping Strategy](./03-web-scraping-strategy.md)
   - Priority targets
   - Technical implementation
   - Ethical considerations

4. [Data Architecture](./04-data-architecture.md)
   - Schema design
   - Deduplication strategy
   - Data validation

5. [Implementation Plan](./05-implementation-plan.md)
   - Development phases
   - Technical architecture
   - Testing approach

6. [Progress Log](./progress-log.md)
   - Detailed chronological record of all work completed

## Project Status

Current phase: Advanced Implementation

We have completed the following milestones:
- Created the repository structure and basic architecture
- Implemented the database schema with SQLAlchemy ORM models
- Developed a FastAPI-based REST API with comprehensive endpoints
- Created base scraper framework with proxy rotation and rate limiting
- Successfully tested core functionality with a SQLite database
- Implemented full data extraction for USA Swimming with real-time parsing
- Added search strategies for swimmers, events, and geographic regions
- Implemented NISCA scraper for high school records and All-America lists
- Integrated multiple data sources with standardized storage formats
- Created robust data parsing and transformation pipelines

## Getting Started

### Prerequisites
- Python 3.9+ (tested with Python 3.13)
- Required packages listed in requirements.txt
- For building some packages: C/C++ compiler (e.g., Microsoft Visual C++ Build Tools)

### Setup and Installation
1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/MacOS
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   python database/setup_db.py --drop
   ```
5. Start the API server:
   ```
   python web/backend/server.py
   ```
6. Access the API documentation at http://localhost:8000/docs

## Testing Status

- **Database Layer**: ✅ Successfully tested with SQLite
- **API Layer**: ✅ All endpoints functional with proper relationships
- **Scraper Layer**: ✅ Multiple scrapers implemented (USA Swimming, NISCA)
- **Frontend Layer**: 📝 Not yet implemented

## Scraper Usage

### USA Swimming Scraper

To test the USA Swimming scraper, you can use the included test script:

```bash
# Search for a specific swimmer
python scrapers/test_scraper.py --test swimmer

# Search for a specific event
python scrapers/test_scraper.py --test event

# Search by state
python scrapers/test_scraper.py --test state

# Run a full scrape with limited scope
python scrapers/test_scraper.py --test full
```

### NISCA Scraper

To test the NISCA scraper for high school records and All-America lists:

```bash
# Test national records scraping
python scrapers/test_nisca_scraper.py --test records

# Test All-America lists scraping
python scrapers/test_nisca_scraper.py --test all_america

# Run a full NISCA scrape
python scrapers/test_nisca_scraper.py --test full
```

### Using the Main Application

You can also run scrapers through the main application:

```bash
# Run USA Swimming scraper
python main.py scrape --name usa_swimming

# Run NISCA scraper
python main.py scrape --name nisca
```

## Repository Structure

```
SwimDataProject/
├── README.md                # Project overview
├── docs/                    # Documentation
│   ├── 01-project-planning.md
│   ├── 02-data-sources.md
│   ├── 03-web-scraping-strategy.md
│   ├── 04-data-architecture.md
│   └── 05-implementation-plan.md
├── scrapers/                # Web scraping code
│   ├── __init__.py
│   ├── base_scraper.py      # Base scraper class
│   └── usa_swimming_scraper.py  # USA Swimming implementation
├── database/                # Database schema and scripts
│   ├── __init__.py
│   ├── database.py          # Database connection utilities
│   ├── models.py            # SQLAlchemy ORM models
│   ├── setup_db.py          # Database initialization
│   └── migrations/          # Alembic migration scripts
├── web/                     # Web application code
│   ├── backend/             # Backend API
│   │   ├── api/             # API routes and models
│   │   ├── config.py        # Backend configuration
│   │   └── server.py        # Server startup script
│   └── frontend/            # Frontend (pending)
├── analysis/                # Data analysis tools (pending)
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignore rules
├── .env.example             # Example environment configuration
└── progress-log.md          # Development progress log
```

## Next Steps

1. Docker containerization for consistent environments
2. Complete the scrapers with actual data extraction logic
3. Set up PostgreSQL for production environment
4. Begin frontend development with React
5. Implement entity resolution for deduplication

## Contributors

- Development Team

## License

This project is proprietary and confidential.
