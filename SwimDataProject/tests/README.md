# Swim Data Project Testing Framework

This directory contains the testing framework for the Swim Data Project scrapers. The framework is designed to provide thorough testing of both individual components and integrated scraper functionality.

## Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test how components work together
- **Fixtures**: Reusable test components and mock data

### Directory Structure

```
tests/
├── fixtures/         # Test fixtures and mock data
│   ├── conftest.py   # Global pytest fixtures
│   └── mock_responses.py  # Mock HTML responses for testing
├── scrapers/         # Tests for scraper modules
│   ├── test_base_scraper.py  # Tests for base scraper classes
│   ├── usa_swimming/  # USA Swimming specific tests
│   │   ├── test_individual_times.py
│   │   ├── test_event_rankings.py
│   │   ├── test_scraper.py
│   │   └── test_integration.py
│   └── test_nisca_scraper.py  # NISCA scraper tests
└── README.md         # This file
```

## Running Tests

### Running All Tests

```bash
cd SwimDataProject
python -m pytest
```

### Running Specific Test Categories

```bash
# Run just the unit tests
python -m pytest -m unit

# Run integration tests
python -m pytest -m integration

# Run just the USA Swimming tests
python -m pytest -m usa_swimming

# Run tests that don't require a real browser
python -m pytest -k "not selenium"
```

### Running Tests With Coverage

```bash
python -m pytest --cov=SwimDataProject
```

## Testing Approach

### Scraper Testing Strategy

1. **Mock External Dependencies**: Tests use mocked web responses and browsers to avoid real web requests during testing.

2. **Layered Testing**: 
   - Test the base components (RateLimiter, ProxyManager, etc.)
   - Test specific scraper modules (individual_times, event_rankings, etc.)
   - Test the orchestration layer (USASwimmingScraper)
   - Test the complete flow (scrape_usa_swimming function)

3. **Test Data Coverage**:
   - Successful scenarios with complete data
   - Error handling scenarios
   - Edge cases with missing or malformed data

### Mocking Strategy

The testing framework uses several mocking strategies:

1. **Mock Web Responses**: HTML response content is mocked to avoid real network requests.

2. **Mock WebDriver**: Selenium WebDriver is mocked for most tests, with optional real WebDriver tests for integration verification.

3. **Mock Logger**: Logging is mocked to test that appropriate messages are logged.

4. **Mock File System**: File saving operations use temporary directories to avoid modifying the real file system.

## Adding New Tests

### Adding a New Scraper Test

1. Create a new test file in the appropriate directory
2. Add mock responses to `fixtures/mock_responses.py` if needed
3. Follow the existing patterns for setup, mocking, and assertions

### Adding a New Test Fixture

1. Add reusable fixtures to the appropriate `conftest.py` file
2. For global fixtures used across many tests, add to `fixtures/conftest.py`
3. For module-specific fixtures, add to a module-specific `conftest.py`

## Test Dependencies

The testing framework requires:

- pytest
- pytest-cov (for coverage reports)
- pytest-mock (for mocking)
- selenium (for WebDriver tests)

See `requirements-test.txt` for a complete list of testing dependencies.
