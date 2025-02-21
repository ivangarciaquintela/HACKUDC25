-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills table
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50),
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(name, version)
);

-- User Skills junction table
CREATE TABLE user_skills (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level INTEGER CHECK (proficiency_level BETWEEN 1 AND 5),
    years_experience NUMERIC(4,1),
    last_used_date DATE,
    PRIMARY KEY (user_id, skill_id)
);

-- Insert test users (password for all users is 'password123')
INSERT INTO users (username, email, password_hash, created_at) VALUES
    ('john_dev', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('maria_tech', 'maria@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('alex_data', 'alex@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('sara_web', 'sara@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('mike_devops', 'mike@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW());

-- Insert programming languages
INSERT INTO skills (name, version, description, category) VALUES
    ('Python', '3.11', 'High-level programming language', 'Programming Languages'),
    ('Python', '3.12', 'Latest Python version with improved features', 'Programming Languages'),
    ('JavaScript', 'ES6+', 'Modern JavaScript with ES6+ features', 'Programming Languages'),
    ('TypeScript', '5.0', 'Typed superset of JavaScript', 'Programming Languages'),
    ('Java', '21', 'Enterprise-grade programming language', 'Programming Languages'),
    ('Go', '1.21', 'High-performance systems programming', 'Programming Languages');

-- Insert frameworks and libraries
INSERT INTO skills (name, version, description, category) VALUES
    ('React', '18.0', 'Frontend JavaScript library', 'Frameworks'),
    ('Angular', '17', 'Full-featured frontend framework', 'Frameworks'),
    ('Django', '5.0', 'Python web framework', 'Frameworks'),
    ('FastAPI', '0.104', 'Modern Python web framework', 'Frameworks'),
    ('Spring Boot', '3.2', 'Java enterprise framework', 'Frameworks'),
    ('Vue.js', '3.0', 'Progressive JavaScript framework', 'Frameworks');

-- Insert databases
INSERT INTO skills (name, version, description, category) VALUES
    ('PostgreSQL', '15', 'Advanced open-source database', 'Databases'),
    ('MongoDB', '7.0', 'NoSQL document database', 'Databases'),
    ('Redis', '7.2', 'In-memory data structure store', 'Databases'),
    ('MySQL', '8.0', 'Popular open-source SQL database', 'Databases');

-- Insert DevOps tools
INSERT INTO skills (name, version, description, category) VALUES
    ('Docker', 'latest', 'Container platform', 'DevOps'),
    ('Kubernetes', 'latest', 'Container orchestration', 'DevOps'),
    ('Git', 'latest', 'Version control system', 'DevOps'),
    ('Jenkins', 'latest', 'Continuous Integration server', 'DevOps'),
    ('AWS', 'latest', 'Cloud platform services', 'Cloud'),
    ('Azure', 'latest', 'Microsoft cloud platform', 'Cloud');

-- Insert user skills (john_dev)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 5, 3.5, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'john_dev' AND s.name IN ('Python', 'JavaScript', 'React', 'PostgreSQL', 'Docker');

-- Insert user skills (maria_tech)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 4, 2.0, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'maria_tech' AND s.name IN ('Java', 'Spring Boot', 'MySQL', 'Git', 'AWS');

-- Insert user skills (alex_data)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 5, 4.0, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'alex_data' AND s.name IN ('Python', 'PostgreSQL', 'MongoDB', 'AWS', 'Docker');

-- Insert user skills (sara_web)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 4, 2.5, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'sara_web' AND s.name IN ('JavaScript', 'TypeScript', 'React', 'Vue.js', 'Git');

-- Insert user skills (mike_devops)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 5, 5.0, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'mike_devops' AND s.name IN ('Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Git');

   
   
