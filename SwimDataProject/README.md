# Swim Data Project

A comprehensive platform for collecting, analyzing, and visualizing swimming data for high school swimmers, allowing them to compare their performance at city, state, regional, national, and international levels.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.21-orange)](https://www.sqlalchemy.org/)

## Project Overview

This project aims to create a data platform that provides high school swimmers with insights about their competitive standing. It collects data from various swimming sources through web scraping, stores it in a structured database, and provides API endpoints and visualizations for analysis.

### Key Features

- Multi-source data collection (USA Swimming, NISCA, state associations, etc.)
- Comprehensive swimmer profiles with times and rankings
- Multi-level comparisons (city, state, regional, national, international)
- Performance analytics and progression tracking
- Comparison of high school swimmers to elite/Olympic swimmers
- Interactive data visualizations

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+ (SQLite for development)
- Chrome/Chromium browser (for Selenium scrapers)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dbaca04/SwimDataProject.git
   cd SwimDataProject
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Initialize the database:
   ```bash
   python main.py init-db
   ```

6. Run a scraper:
   ```bash
   python main.py scrape --name usa_swimming
   ```

7. Start the API server:
   ```bash
   python main.py api
   ```

8. Access the API documentation:
   - Open a browser and navigate to http://localhost:8000/docs

For more detailed setup instructions, see [Getting Started](./getting-started.md).

## Project Structure

```
SwimDataProject/
├── scrapers/                # Web scraping modules
│   ├── base_scraper.py      # Base scraper class
│   ├── usa_swimming_scraper.py  # USA Swimming implementation
│   └── nisca_scraper.py     # NISCA implementation
├── database/                # Database schema and operations
│   ├── database.py          # Database connection utilities
│   ├── models.py            # SQLAlchemy ORM models
│   └── setup_db.py          # Database initialization
├── web/                     # Web application code
│   ├── backend/             # Backend API
│   │   ├── api/             # API routes and models
│   │   ├── config.py        # Backend configuration
│   │   └── server.py        # Server startup script
│   └── frontend/            # Frontend (in development)
├── analysis/                # Data analysis tools
├── main.py                  # Main entry point
└── docs/                    # Project documentation
    ├── 01-project-planning.md
    ├── 02-data-sources.md
    ├── 03-web-scraping-strategy.md
    ├── 04-data-architecture.md
    ├── 05-implementation-plan.md
    └── progress-log.md
```

## Data Sources

The project collects data from multiple sources:

1. **USA Swimming**: Official database for USA Swimming with sanctioned meet results
2. **NISCA**: National Interscholastic Swim Coaches Association records and rankings
3. **State Athletic Associations**: State-level competition results
4. **SwimCloud**: Additional rankings and analytics
5. **SwimStandards**: Time standards and additional profiles
6. **SwimRankings.net**: International comparison data

## Development Status

Current phase: Initial Implementation and Testing

- [x] Repository structure and architecture
- [x] Database schema with SQLAlchemy ORM models
- [x] FastAPI-based REST API with comprehensive endpoints
- [x] Base scraper framework with proxy rotation and rate limiting
- [x] USA Swimming scraper implementation
- [x] NISCA scraper implementation
- [ ] Frontend development with React
- [ ] Advanced analytics and visualization

## Testing

Run tests using pytest:

```bash
pytest
```

For more information on testing, see [Testing Notes](./testing-notes.md).

## Documentation

- [Project Planning](./01-project-planning.md)
- [Data Sources Analysis](./02-data-sources.md)
- [Web Scraping Strategy](./03-web-scraping-strategy.md)
- [Data Architecture](./04-data-architecture.md)
- [Implementation Plan](./05-implementation-plan.md)
- [Progress Log](./progress-log.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
