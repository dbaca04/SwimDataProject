# Swim Data Project Repository Structure

This is the code repository for the Swim Data Project, which aims to create a comprehensive swimming data platform focused on high school swimmers.

## Repository Structure

```
SwimDataProject/
├── scrapers/              # Web scraping modules
│   ├── __init__.py
│   ├── base_scraper.py    # Base scraper class
│   └── usa_swimming_scraper.py  # USA Swimming specific scraper
│
├── database/              # Database modules and migrations
│   ├── __init__.py
│   ├── database.py        # Database connection utilities
│   ├── models.py          # SQLAlchemy ORM models
│   ├── setup_db.py        # Database initialization script
│   └── migrations/        # Alembic migration scripts
│       ├── env.py
│       ├── script.py.mako
│       ├── alembic.ini
│       └── versions/      # Migration version files
│
├── analysis/              # Data analysis tools
│
├── web/                   # Web application code
│   ├── backend/           # Backend API
│   │   ├── api/           # API routes and models
│   │   │   ├── __init__.py
│   │   │   ├── main.py    # FastAPI application
│   │   │   ├── models.py  # Pydantic models for API
│   │   │   └── routes/    # API route modules
│   │   │       ├── __init__.py
│   │   │       ├── swimmers.py
│   │   │       ├── times.py
│   │   │       ├── rankings.py
│   │   │       ├── events.py
│   │   │       └── teams.py
│   │   ├── config.py      # Backend configuration
│   │   └── server.py      # Server startup script
│   └── frontend/          # Frontend application (to be added)
│
├── docs/                  # Project documentation
│   ├── 01-project-planning.md
│   ├── 02-data-sources.md
│   ├── 03-web-scraping-strategy.md
│   ├── 04-data-architecture.md
│   ├── 05-implementation-plan.md
│   └── progress-log.md
│
├── README.md              # Project overview
├── README_REPO.md         # Repository structure documentation (this file)
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore file
└── .env.example           # Example environment configuration
```

## Technology Stack

This project uses the following technologies:

### Backend
- **Python 3.9+**: Main programming language
- **FastAPI**: Web API framework
- **SQLAlchemy**: ORM for database access
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

### Database
- **PostgreSQL**: Primary database (SQLite for development)

### Web Scraping
- **Requests**: HTTP client
- **BeautifulSoup4**: HTML parsing
- **Selenium**: Browser automation
- **Scrapy**: Advanced web scraping (optional)

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical operations
- **scikit-learn**: Machine learning for entity resolution
- **FuzzyWuzzy**: Fuzzy string matching

### Frontend (Planned)
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Recharts**: Data visualization

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone [repository URL]
   cd SwimDataProject
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize the database**:
   ```bash
   python database/setup_db.py --drop
   ```

6. **Start the API server**:
   ```bash
   python web/backend/server.py
   ```

7. **Access the API documentation**:
   - Open a browser and navigate to http://localhost:8000/docs

## Next Steps

1. Implement the remaining scrapers for other data sources
2. Develop the entity resolution system for deduplication
3. Create the frontend application
4. Implement advanced analytics features
