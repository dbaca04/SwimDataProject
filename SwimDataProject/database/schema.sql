-- SwimDataProject Database Schema

-- Core Tables

-- 1. Swimmers
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

-- 2. Swimmer Aliases
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

-- 3. Teams/Schools
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

-- 4. Team Aliases
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

-- 5. Swimmer-Team Affiliations
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

-- 6. Events
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

-- 7. Event Aliases
CREATE TABLE event_aliases (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name_alias VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, name_alias, source)
);

CREATE INDEX idx_event_aliases_name ON event_aliases(name_alias);

-- 8. Meets
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

-- 9. Swim Times
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

-- 10. Rankings
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

-- 11. Time Standards
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

-- 12. Data Sources
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

-- 13. Source Mapping
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

-- Auxiliary Tables

-- 1. Comparison Records
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

-- 2. Swimmer Progress
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

-- 3. Record Tracking
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

-- 4. System Logs
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    log_type VARCHAR(50) NOT NULL, -- 'error', 'warning', 'info', 'merge', etc.
    entity_type VARCHAR(50), -- 'swimmer', 'team', 'meet', etc.
    entity_id INT,
    related_entity_id INT,
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_type ON system_logs(log_type);
CREATE INDEX idx_logs_entity ON system_logs(entity_type, entity_id);
CREATE INDEX idx_logs_created ON system_logs(created_at);

-- 5. Data Quality Metrics
CREATE TABLE data_quality_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- 'swimmer', 'team', 'meet', etc.
    value NUMERIC(10, 2) NOT NULL,
    threshold NUMERIC(10, 2),
    status VARCHAR(20) NOT NULL, -- 'good', 'warning', 'critical', etc.
    details JSONB,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quality_metric ON data_quality_metrics(metric_name);
CREATE INDEX idx_quality_entity ON data_quality_metrics(entity_type);
CREATE INDEX idx_quality_status ON data_quality_metrics(status);
CREATE INDEX idx_quality_date ON data_quality_metrics(measured_at);

-- 6. User Flagged Data
CREATE TABLE user_flagged_data (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'swimmer', 'team', 'time', etc.
    entity_id INT NOT NULL,
    flag_type VARCHAR(50) NOT NULL, -- 'incorrect', 'duplicate', 'missing', etc.
    user_id INT, -- If user authentication is implemented
    user_email VARCHAR(255),
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'resolved', 'rejected', etc.
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flagged_entity ON user_flagged_data(entity_type, entity_id);
CREATE INDEX idx_flagged_status ON user_flagged_data(status);
CREATE INDEX idx_flagged_date ON user_flagged_data(created_at);

-- 7. Static Data Tables

-- Event Type Reference
CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    stroke VARCHAR(50) NOT NULL UNIQUE,
    abbreviation VARCHAR(10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard strokes
INSERT INTO event_types (stroke, abbreviation, description) VALUES
('freestyle', 'FR', 'Freestyle'),
('backstroke', 'BK', 'Backstroke'),
('breaststroke', 'BR', 'Breaststroke'),
('butterfly', 'FL', 'Butterfly'),
('individual_medley', 'IM', 'Individual Medley');

-- Course Type Reference
CREATE TABLE course_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard course types
INSERT INTO course_types (code, name, description) VALUES
('SCY', 'Short Course Yards', '25 yard pool'),
('SCM', 'Short Course Meters', '25 meter pool'),
('LCM', 'Long Course Meters', '50 meter pool');

-- State/Region Reference
CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    code VARCHAR(2) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    lsc_code VARCHAR(10),
    lsc_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial Static Data

-- Insert standard events for SCY
INSERT INTO events (name, distance, stroke, course, is_relay, standard_name) VALUES
('50 Freestyle', 50, 'freestyle', 'SCY', FALSE, '50 Freestyle SCY'),
('100 Freestyle', 100, 'freestyle', 'SCY', FALSE, '100 Freestyle SCY'),
('200 Freestyle', 200, 'freestyle', 'SCY', FALSE, '200 Freestyle SCY'),
('500 Freestyle', 500, 'freestyle', 'SCY', FALSE, '500 Freestyle SCY'),
('1000 Freestyle', 1000, 'freestyle', 'SCY', FALSE, '1000 Freestyle SCY'),
('1650 Freestyle', 1650, 'freestyle', 'SCY', FALSE, '1650 Freestyle SCY'),
('100 Backstroke', 100, 'backstroke', 'SCY', FALSE, '100 Backstroke SCY'),
('200 Backstroke', 200, 'backstroke', 'SCY', FALSE, '200 Backstroke SCY'),
('100 Breaststroke', 100, 'breaststroke', 'SCY', FALSE, '100 Breaststroke SCY'),
('200 Breaststroke', 200, 'breaststroke', 'SCY', FALSE, '200 Breaststroke SCY'),
('100 Butterfly', 100, 'butterfly', 'SCY', FALSE, '100 Butterfly SCY'),
('200 Butterfly', 200, 'butterfly', 'SCY', FALSE, '200 Butterfly SCY'),
('200 Individual Medley', 200, 'individual_medley', 'SCY', FALSE, '200 Individual Medley SCY'),
('400 Individual Medley', 400, 'individual_medley', 'SCY', FALSE, '400 Individual Medley SCY');

-- Insert standard data sources
INSERT INTO data_sources (name, url, description, scrape_frequency, active) VALUES
('usa_swimming', 'https://data.usaswimming.org', 'USA Swimming data hub for individual times and rankings', 'daily', TRUE),
('nisca', 'https://niscaonline.org', 'National Interscholastic Swim Coaches Association records and rankings', 'weekly', TRUE),
('swimcloud', 'https://www.swimcloud.com', 'SwimCloud rankings and results platform', 'weekly', TRUE),
('swimstandards', 'https://swimstandards.com', 'SwimStandards time standards and profiles', 'monthly', TRUE);
