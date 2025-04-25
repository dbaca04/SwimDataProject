# Getting Started with Swim Data Project

This guide will help you set up your development environment and run the Swim Data Project locally.

## Prerequisites

1. **Python Environment**:
   - Python 3.9+ installed (3.9 or 3.10 recommended for best compatibility)
   - Ability to create virtual environments
   - Pip package manager

2. **Development Tools**:
   - Git for version control
   - Visual Studio Code or your preferred IDE
   - For Windows: Microsoft Visual C++ Build Tools (for compiling certain packages)

3. **Optional**:
   - Docker and Docker Compose (for containerized development)
   - PostgreSQL (for production-like database testing)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SwimDataProject
```

### 2. Create a Virtual Environment

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter build errors with pandas or other packages that require compilation, try:
1. Install only the core packages first:
   ```bash
   pip install requests beautifulsoup4 fastapi uvicorn sqlalchemy python-dotenv pydantic-settings
   ```
2. Install Microsoft Visual C++ Build Tools (Windows) or equivalent on other platforms
3. Try installing the remaining packages after build tools are installed

### 4. Configure Environment

Create a `.env` file in the project root based on the provided example:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment:
- For development, the default SQLite configuration should work fine
- For production-like testing, configure PostgreSQL connection

### 5. Initialize the Database

```bash
python database/setup_db.py --drop
```

This will:
- Create the database schema
- Populate it with seed data for testing
- The `--drop` flag will drop any existing database first (use with caution)

### 6. Start the API Server

```bash
python web/backend/server.py
```

The server will start on http://localhost:8000 by default. You can access:
- API Documentation: http://localhost:8000/docs
- Alternative API Documentation: http://localhost:8000/redoc
- API Root: http://localhost:8000/api/

## Testing the API

You can test the API using curl, Postman, or any HTTP client:

### Example Requests:

#### Get All Swimmers:
```bash
curl -X GET "http://localhost:8000/api/swimmers"
```

#### Get Specific Swimmer:
```bash
curl -X GET "http://localhost:8000/api/swimmers/1"
```

#### Get All Events:
```bash
curl -X GET "http://localhost:8000/api/events"
```

#### Get Swim Times:
```bash
curl -X GET "http://localhost:8000/api/times"
```

## Running Scrapers

The scraper framework is set up, but actual data extraction is not yet implemented. To test the basic scraper structure:

```bash
# Not yet implemented - future functionality
# python -m scrapers.usa_swimming_scraper
```

## Development Workflow

1. **Code Organization**:
   - Keep code modular and focused
   - Follow the established project structure
   - Use appropriate abstractions for each layer

2. **Dependencies**:
   - Add new dependencies to `requirements.txt`
   - Consider compatibility with Python versions
   - Document any special installation requirements

3. **Database Changes**:
   - Update models in `database/models.py`
   - For schema changes, create migration scripts (future)
   - Test changes with `setup_db.py` before committing

4. **API Development**:
   - Add new routes in appropriate route modules
   - Define request/response models in `models.py`
   - Document API endpoints with FastAPI docstrings

5. **Testing**:
   - Manual testing through API endpoints
   - Use the FastAPI documentation UI for interactive testing
   - Add automated tests (future)

## Common Issues

### Package Installation Failures

**Issue**: Packages that require C extensions fail to build
**Solution**: Install appropriate build tools for your platform
- Windows: Microsoft Visual C++ Build Tools
- macOS: Xcode Command Line Tools
- Linux: gcc, python3-dev, etc.

### Database Connection Issues

**Issue**: Unable to connect to the database
**Solutions**:
- For SQLite: Check file paths and permissions
- For PostgreSQL: Verify connection parameters in `.env`
- Check if you're using the correct database URL format

### API Server Won't Start

**Issue**: Errors when starting the API server
**Solutions**:
- Check for syntax errors in Python code
- Verify that all dependencies are installed
- Look for import errors in the traceback
- Ensure the correct Python version is being used

## Next Steps

1. **Complete the scrapers**:
   - Add actual data extraction logic
   - Implement data transformation
   - Test against live data sources

2. **Set up Docker**:
   - Create Docker configuration for consistent environments
   - Set up multi-container Docker Compose

3. **Frontend development**:
   - Create the React-based frontend
   - Implement data visualization components

4. **Production preparation**:
   - Configure PostgreSQL
   - Set up authentication
   - Implement performance optimizations
