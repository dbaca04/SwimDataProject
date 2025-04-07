# USA Swim Data Project

A comprehensive platform for collecting, analyzing, and visualizing swimming data for high school swimmers, allowing them to compare their performance at city, state, regional, national, and international levels.

## Project Overview

This project aims to create a data platform that provides high school swimmers with insights about their competitive standing. It collects data from various swimming sources through web scraping, stores it in a structured database, and provides API endpoints and visualizations for analysis.

## Key Features

- Multi-source data collection (USA Swimming, NISCA, state associations, etc.)
- Comprehensive swimmer profiles with times and rankings
- Multi-level comparisons (city, state, regional, national, international)
- Performance analytics and progression tracking
- Comparison of high school swimmers to elite/Olympic swimmers
- Interactive data visualizations

## Repository Structure

```
SwimDataProject/
├── api/                    # API endpoints and server
├── config/                 # Configuration settings
├── database/               # Database schema and operations
├── scrapers/               # Web scraping modules
├── web/                    # Frontend application
├── main.py                 # Main entry point
└── README.md               # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Chrome/Chromium browser (for Selenium scrapers)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/usa-swim.git
   cd usa-swim
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python main.py init-db
   ```

4. Run a scraper:
   ```
   python main.py scrape --name usa_swimming
   ```

5. Start the API server:
   ```
   python main.py api
   ```

## Documentation

- [Project Planning](./SwimDataProject/01-project-planning.md)
- [Data Sources Analysis](./SwimDataProject/02-data-sources.md)
- [Web Scraping Strategy](./SwimDataProject/03-web-scraping-strategy.md)
- [Data Architecture](./SwimDataProject/04-data-architecture.md)
- [Implementation Plan](./SwimDataProject/05-implementation-plan.md)
- [Progress Log](./SwimDataProject/progress-log.md)

## Data Sources

The project collects data from multiple sources:

1. **USA Swimming**: Official database for USA Swimming with sanctioned meet results
2. **NISCA**: National Interscholastic Swim Coaches Association records and rankings
3. **State Athletic Associations**: State-level competition results
4. **SwimCloud**: Additional rankings and analytics
5. **SwimStandards**: Time standards and additional profiles
6. **SwimRankings.net**: International comparison data

## Contributing

This project is currently in the planning and initial development phase. Contributions are welcome through pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
