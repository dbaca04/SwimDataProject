# Data Architecture

This document outlines the database schema, data storage approach, and data quality management strategy for the swimming data platform.

## Database Schema

Our database schema is designed to handle the diverse and often inconsistent data from multiple swimming data sources while providing a unified view for analysis and presentation.

### Core Tables

#### 1. Swimmers

```sql
CREATE TABLE swimmers (
    id SERIAL PRIMARY KEY,
    primary_name VARCHAR(255) NOT NULL,
    gender CHAR(1),
    birth_year INT,
    current_age INT,
    last_computed_age_date DATE,
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_swimmers_name ON swimmers(primary_name);
CREATE INDEX idx_swimmers_gender ON swimmers(gender);
CREATE INDEX idx_swimmers_birth_year ON swimmers(birth_year);
CREATE INDEX idx_swimmers_state ON swimmers(state);
```

#### 2. Swimmer Aliases

```sql
CREATE TABLE swimmer_aliases (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    name_alias VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (swimmer_id, name_alias)
);

CREATE INDEX idx_swimmer_aliases_name ON swimmer_aliases(name_alias);
```

#### 3. Teams/Schools

```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    type VARCHAR(50) NOT NULL, -- 'high_school', 'club', 'college', etc.
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_state ON teams(state);
CREATE INDEX idx_teams_type ON teams(type);
```

#### 4. Team Aliases

```sql
CREATE TABLE team_aliases (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name_alias VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (team_id, name_alias)
);

CREATE INDEX idx_team_aliases_name ON team_aliases(name_alias);
```

#### 5. Swimmer-Team Affiliations

```sql
CREATE TABLE swimmer_team_affiliations (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    source VARCHAR(100),
    source_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_affiliations_swimmer ON swimmer_team_affiliations(swimmer_id);
CREATE INDEX idx_affiliations_team ON swimmer_team_affiliations(team_id);
CREATE INDEX idx_affiliations_current ON swimmer_team_affiliations(is_current);
```

#### 6. Events

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    distance INT NOT NULL,
    stroke VARCHAR(50) NOT NULL, -- 'freestyle', 'backstroke', etc.
    course VARCHAR(10) NOT NULL, -- 'SCY', 'SCM', 'LCM'
    is_relay BOOLEAN DEFAULT FALSE,
    standard_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (distance, stroke, course, is_relay)
);

CREATE INDEX idx_events_distance ON events(distance);
CREATE INDEX idx_events_stroke ON events(stroke);
CREATE INDEX idx_events_course ON events(course);
CREATE INDEX idx_events_standard_name ON events(standard_name);
```

#### 7. Event Aliases

```sql
CREATE TABLE event_aliases (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name_alias VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, name_alias, source)
);

CREATE INDEX idx_event_aliases_name ON event_aliases(name_alias);
```

#### 8. Meets

```sql
CREATE TABLE meets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    course VARCHAR(10), -- 'SCY', 'SCM', 'LCM'
    host VARCHAR(255),
    meet_type VARCHAR(100), -- 'high_school', 'club', 'championship', etc.
    is_observed BOOLEAN DEFAULT FALSE,
    source VARCHAR(100),
    source_id VARCHAR(100),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meets_name ON meets(name);
CREATE INDEX idx_meets_date ON meets(start_date, end_date);
CREATE INDEX idx_meets_type ON meets(meet_type);
CREATE INDEX idx_meets_source ON meets(source, source_id);
```

#### 9. Swim Times

```sql
CREATE TABLE swim_times (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    meet_id INT REFERENCES meets(id) ON DELETE SET NULL,
    team_id INT REFERENCES teams(id) ON DELETE SET NULL,
    time_seconds NUMERIC(10, 2) NOT NULL,
    time_formatted VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    swimmer_age INT,
    is_relay_leadoff BOOLEAN DEFAULT FALSE,
    is_split BOOLEAN DEFAULT FALSE,
    source VARCHAR(100) NOT NULL,
    source_id VARCHAR(100),
    source_url TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_times_swimmer ON swim_times(swimmer_id);
CREATE INDEX idx_times_event ON swim_times(event_id);
CREATE INDEX idx_times_date ON swim_times(date);
CREATE INDEX idx_times_time ON swim_times(time_seconds);
CREATE INDEX idx_times_source ON swim_times(source, source_id);
```

#### 10. Rankings

```sql
CREATE TABLE rankings (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    time_id INT REFERENCES swim_times(id) ON DELETE CASCADE,
    rank INT NOT NULL,
    time_seconds NUMERIC(10, 2) NOT NULL,
    rank_scope VARCHAR(50) NOT NULL, -- 'national', 'state', 'age_group', etc.
    rank_scope_value VARCHAR(100), -- For state: 'CA', for age_group: '15-16', etc.
    season VARCHAR(20), -- '2023-2024', etc.
    as_of_date DATE NOT NULL,
    source VARCHAR(100) NOT NULL,
    source_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rankings_swimmer ON rankings(swimmer_id);
CREATE INDEX idx_rankings_event ON rankings(event_id);
CREATE INDEX idx_rankings_rank ON rankings(rank);
CREATE INDEX idx_rankings_scope ON rankings(rank_scope, rank_scope_value);
CREATE INDEX idx_rankings_season ON rankings(season);
CREATE INDEX idx_rankings_date ON rankings(as_of_date);
```

#### 11. Time Standards

```sql
CREATE TABLE time_standards (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    standard_name VARCHAR(100) NOT NULL, -- 'AAAA', 'AAA', 'AA', etc. or 'Futures', 'Junior National', etc.
    gender CHAR(1) NOT NULL,
    age_group VARCHAR(20) NOT NULL, -- '11-12', '13-14', '15-16', '17-18', 'Open', etc.
    time_seconds NUMERIC(10, 2) NOT NULL,
    time_formatted VARCHAR(20) NOT NULL,
    season VARCHAR(20), -- '2023-2024', etc.
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_standards_event ON time_standards(event_id);
CREATE INDEX idx_standards_name ON time_standards(standard_name);
CREATE INDEX idx_standards_gender ON time_standards(gender);
CREATE INDEX idx_standards_age ON time_standards(age_group);
CREATE INDEX idx_standards_season ON time_standards(season);
```

#### 12. Data Sources

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(255),
    description TEXT,
    last_scraped TIMESTAMP,
    scrape_frequency VARCHAR(50), -- 'daily', 'weekly', 'monthly', etc.
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 13. Source Mapping

```sql
CREATE TABLE source_mapping (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'swimmer', 'team', 'meet', etc.
    entity_id INT NOT NULL,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source, source_id, entity_type)
);

CREATE INDEX idx_source_mapping_source ON source_mapping(source, source_id);
CREATE INDEX idx_source_mapping_entity ON source_mapping(entity_type, entity_id);
```

### Auxiliary Tables

#### 1. Comparison Records

```sql
CREATE TABLE comparison_records (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    comparison_type VARCHAR(50) NOT NULL, -- 'high_school_to_olympic', 'age_group_progression', etc.
    current_time_seconds NUMERIC(10, 2) NOT NULL,
    comparison_value NUMERIC(10, 2) NOT NULL, -- Different meaning based on comparison_type
    comparison_percentage NUMERIC(5, 2) NOT NULL, -- Percentage difference
    reference_entity VARCHAR(255), -- Could be Olympic swimmer name, age group, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comparison_swimmer ON comparison_records(swimmer_id);
CREATE INDEX idx_comparison_event ON comparison_records(event_id);
CREATE INDEX idx_comparison_type ON comparison_records(comparison_type);
```

#### 2. Swimmer Progress

```sql
CREATE TABLE swimmer_progress (
    id SERIAL PRIMARY KEY,
    swimmer_id INT NOT NULL REFERENCES swimmers(id) ON DELETE CASCADE,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    time_period VARCHAR(50) NOT NULL, -- '30_days', '90_days', '1_year', etc.
    start_time_seconds NUMERIC(10, 2) NOT NULL,
    end_time_seconds NUMERIC(10, 2) NOT NULL,
    improvement_seconds NUMERIC(10, 2) NOT NULL,
    improvement_percentage NUMERIC(5, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_progress_swimmer ON swimmer_progress(swimmer_id);
CREATE INDEX idx_progress_event ON swimmer_progress(event_id);
CREATE INDEX idx_progress_period ON swimmer_progress(time_period);
```

#### 3. Record Tracking

```sql
CREATE TABLE records (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    record_type VARCHAR(100) NOT NULL, -- 'national_age_group', 'state_high_school', etc.
    scope VARCHAR(100), -- State code, age group, etc.
    gender CHAR(1) NOT NULL,
    swimmer_id INT REFERENCES swimmers(id) ON DELETE SET NULL,
    swimmer_name VARCHAR(255), -- In case swimmer not in database
    team_id INT REFERENCES teams(id) ON DELETE SET NULL,
    team_name VARCHAR(255), -- In case team not in database
    time_seconds NUMERIC(10, 2) NOT NULL,
    time_formatted VARCHAR(20) NOT NULL,
    record_date DATE,
    source VARCHAR(100) NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_records_event ON records(event_id);
CREATE INDEX idx_records_type ON records(record_type, scope);
CREATE INDEX idx_records_gender ON records(gender);
CREATE INDEX idx_records_current ON records(is_current);
```

## Data Storage Strategy

### 1. Data Normalization

- **Entity Resolution**: We'll use sophisticated matching algorithms to identify and link the same swimmers, teams, and events across different data sources.
- **Standard Formats**: All times will be stored in both seconds (numeric) and formatted text for easy retrieval.
- **Event Standardization**: Events will be normalized to standard names, distances, and course types.
- **Course Conversion**: Where appropriate, we'll store conversion factors between different course types (SCY, SCM, LCM).

### 2. Historical Data Preservation

- **Temporal Data**: We'll maintain historical rankings, team affiliations, and records with effective dates.
- **Source Attribution**: All data points will maintain references to their original sources.
- **Change Tracking**: Major data changes will be logged for audit purposes.
- **Snapshots**: Regular snapshots of rankings and records will be taken to enable historical analysis.

### 3. Storage Efficiency

- **Data Partitioning**: Time-series data like swim times will be partitioned by time periods.
- **Archiving Strategy**: Older, less frequently accessed data will be moved to cold storage.
- **Caching Layer**: Frequently accessed data (current rankings, recent times) will be cached for performance.
- **Compression**: Historical data will be compressed to save storage space.

## Data Validation and Quality

### 1. Validation Rules

#### Swimmer Data Validation

```python
def validate_swimmer(swimmer_data):
    """Validate swimmer data against business rules"""
    errors = []
    warnings = []
    
    # Required fields
    if not swimmer_data.get('name'):
        errors.append("Swimmer name is required")
    
    # Gender validation
    gender = swimmer_data.get('gender')
    if gender and gender not in ['M', 'F', 'O']:
        errors.append("Gender must be 'M', 'F', or 'O'")
    
    # Birth year validation
    birth_year = swimmer_data.get('birth_year')
    current_year = datetime.datetime.now().year
    if birth_year:
        if not (1920 <= birth_year <= current_year):
            errors.append(f"Birth year must be between 1920 and {current_year}")
    
    # Age validation based on birth year
    if birth_year and swimmer_data.get('age'):
        expected_age_range = (current_year - birth_year - 1, current_year - birth_year)
        if swimmer_data['age'] not in expected_age_range:
            warnings.append("Age doesn't match birth year")
    
    return errors, warnings
```

#### Time Data Validation

```python
def validate_time(time_data):
    """Validate swim time against business rules and physical limits"""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['swimmer_id', 'event_id', 'time_seconds', 'date']
    for field in required_fields:
        if not time_data.get(field):
            errors.append(f"Field '{field}' is required")
    
    if errors:
        return errors, warnings
    
    # Time range validation
    event = get_event(time_data['event_id'])
    min_time, max_time = get_event_time_bounds(event)
    
    if time_data['time_seconds'] < min_time:
        errors.append(f"Time {time_data['time_seconds']} is faster than the world record {min_time}")
    
    if time_data['time_seconds'] > max_time:
        warnings.append(f"Time {time_data['time_seconds']} is unusually slow for this event")
    
    # Date validation
    if time_data['date'] > datetime.datetime.now().date():
        errors.append("Time date cannot be in the future")
    
    # Check for dramatic improvement
    last_times = get_recent_times(time_data['swimmer_id'], time_data['event_id'], limit=5)
    if last_times:
        avg_time = sum(t['time_seconds'] for t in last_times) / len(last_times)
        improvement = avg_time - time_data['time_seconds']
        improvement_pct = improvement / avg_time * 100
        
        if improvement_pct > 10:  # More than 10% improvement
            warnings.append(f"Unusually large improvement ({improvement_pct:.1f}%) from recent average")
    
    return errors, warnings
```

### 2. Deduplication Strategy

Our deduplication strategy involves a multi-stage process to identify and merge duplicate swimmer records:

#### Identification of Potential Duplicates

We use several matching criteria:
- Exact name matches with similar attributes
- Fuzzy name matching with TF-IDF and Levenshtein distance
- Same team affiliations
- Similar swim times at the same meets
- Similar rankings for the same events

#### Scoring and Thresholds

Each potential match is scored based on:
- Name similarity (60% weight)
- Gender match (10% weight)
- Birth year proximity (15% weight)
- Team overlap (15% weight)

Matches with a score above 0.85 are flagged for potential merging.

#### Manual and Automated Resolution

- High-confidence matches (>0.95) can be automatically merged
- Medium-confidence matches (0.85-0.95) require manual review
- All merges maintain a full audit trail
- Original source IDs are preserved through the source_mapping table

### 3. Data Quality Monitoring

Our data quality monitoring system includes:

#### Automated Quality Checks

- Missing data detection across critical fields
- Outlier detection for swim times
- Consistency checks across related records
- Time standard validation against published standards

#### Quality Metrics

- Completeness: Percentage of records with all critical fields populated
- Accuracy: Rate of times falling within expected ranges
- Consistency: Rate of matching data across related records
- Timeliness: Currency of data relative to source updates

#### Reporting and Alerting

- Daily quality reports for operations team
- Automated alerts for quality metrics falling below thresholds
- Quality dashboards showing trends over time
- Detailed error logs for investigation

## Data Integration Patterns

### 1. Source Data Integration

For each data source, we follow this integration pattern:

1. **Extract**: Scrape/retrieve data using source-specific adapters
2. **Transform**: 
   - Normalize entity names (swimmers, teams, events)
   - Standardize time formats
   - Resolve entity references
   - Apply validation rules
3. **Load**: 
   - Store in staging tables
   - Apply deduplication
   - Merge with existing records
   - Update source mappings

### 2. Incremental Updates

Most sources will be processed incrementally:

1. Track last successful scrape timestamp
2. Only process new/changed records since last update
3. Apply intelligent conflict resolution for changes:
   - Prefer more recent data for factual attributes
   - Preserve multiple values for subjective attributes
   - Never overwrite verified data with unverified data

### 3. Data Lineage

For all data points, we maintain lineage information:
- Original source identifier
- Source URL where applicable
- Timestamp of acquisition
- Processing steps applied

This enables:
- Audit capability
- Source verification
- Selective reprocessing of data
- Attribution in user interface

## Database Implementation

### 1. Technology Selection

#### Primary Database: PostgreSQL
- Benefits:
  - Advanced indexing for complex queries
  - JSON support for flexible attributes
  - Full-text search capabilities
  - Strong transaction support
  - Partitioning for time-series data

#### Caching Layer: Redis
- Benefits:
  - High-performance for frequent lookups
  - Support for complex data structures
  - Expiration policies for time-sensitive data
  - Pub/sub for real-time updates

### 2. Performance Considerations

- **Query Optimization**:
  - Selective indexing for common query patterns
  - Materialized views for complex aggregations
  - Denormalization for frequently accessed joins
  
- **Scalability**:
  - Vertical scaling for initial deployment
  - Horizontal read scaling via replicas
  - Data partitioning for large tables
  - Archive strategy for historical data

### 3. Backup and Recovery

- Daily full backups
- Continuous WAL archiving
- Point-in-time recovery capability
- Regular recovery testing
- Multi-region backup storage

## Data Access Patterns

### 1. API Design

Our API will provide standardized access to the database with these core endpoints:

- `/api/swimmers` - Swimmer profiles and related data
- `/api/times` - Time search and filtering
- `/api/rankings` - Rankings across different scopes
- `/api/comparisons` - Comparison analytics
- `/api/standards` - Time standards and qualification data

### 2. Query Optimization

For common query patterns, we'll implement:

- Materialized views for rankings
- Denormalized swimmer profiles
- Pre-computed comparison metrics
- Time-based partitioning for historical data

### 3. Access Control

- Read-only public access for general data
- Authentication for personal data views
- Admin access for data corrections and maintenance
- API rate limiting to prevent abuse

## Implementation Plan

### Phase 1: Core Schema Implementation

1. Implement base tables (swimmers, events, times, teams)
2. Set up initial indexes
3. Create validation rules
4. Implement entity resolution logic

### Phase 2: Data Integration

1. Develop source-specific scrapers
2. Implement ETL pipelines
3. Create initial data load process
4. Establish incremental update procedures

### Phase 3: Quality and Performance

1. Implement data quality monitoring
2. Create performance-optimized views
3. Set up caching layer
4. Establish backup procedures

### Phase 4: Advanced Analytics

1. Implement comparison logic
2. Create progress tracking
3. Develop predictive models
4. Build analytics API endpoints
