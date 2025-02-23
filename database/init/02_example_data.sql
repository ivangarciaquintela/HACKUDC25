-- Insert test users (password for all users is 'password123', except xan which is 'admin')
INSERT INTO users (username, email, password_hash, created_at) VALUES
    ('xan', 'admin@admin.com', '$2b$12$I6mAzOFM06OpfYeqCFndLe7VkQv2adjszcGAe83EsYNCjdEKl0rXG', NOW()),
    ('john_dev', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('maria_tech', 'maria@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('alex_data', 'alex@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('sara_web', 'sara@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('mike_devops', 'mike@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('emma_frontend', 'emma@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('david_backend', 'david@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('lisa_mobile', 'lisa@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('carlos_security', 'carlos@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW()),
    ('ana_data', 'ana@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZoLUYH4ex3G', NOW());

-- Insert programming languages
INSERT INTO skills (name, version, description, category) VALUES
    ('Python', '3.11', 'High-level programming language', 'Programming Languages'),
    ('Python', '3.12', 'Latest Python version with improved features', 'Programming Languages'),
    ('JavaScript', 'ES6+', 'Modern JavaScript with ES6+ features', 'Programming Languages'),
    ('TypeScript', '5.0', 'Typed superset of JavaScript', 'Programming Languages'),
    ('Java', '21', 'Enterprise-grade programming language', 'Programming Languages'),
    ('Go', '1.21', 'High-performance systems programming', 'Programming Languages'),
    ('Swift', '5.9', 'Apple''s programming language', 'Programming Languages'),
    ('Kotlin', '1.9', 'Modern programming language for Android', 'Programming Languages'),
    ('Rust', '1.74', 'Systems programming language', 'Programming Languages');

-- Insert frameworks and libraries
INSERT INTO skills (name, version, description, category) VALUES
    ('React', '18.0', 'Frontend JavaScript library', 'Frameworks'),
    ('Angular', '17', 'Full-featured frontend framework', 'Frameworks'),
    ('Django', '5.0', 'Python web framework', 'Frameworks'),
    ('FastAPI', '0.104', 'Modern Python web framework', 'Frameworks'),
    ('Spring Boot', '3.2', 'Java enterprise framework', 'Frameworks'),
    ('Vue.js', '3.0', 'Progressive JavaScript framework', 'Frameworks'),
    ('NextJS', '14', 'React framework for production', 'Frameworks'),
    ('Flutter', '3.16', 'UI toolkit for mobile development', 'Frameworks');

-- Insert databases
INSERT INTO skills (name, version, description, category) VALUES
    ('PostgreSQL', '15', 'Advanced open-source database', 'Databases'),
    ('MongoDB', '7.0', 'NoSQL document database', 'Databases'),
    ('Redis', '7.2', 'In-memory data structure store', 'Databases'),
    ('MySQL', '8.0', 'Popular open-source SQL database', 'Databases'),
    ('ElasticSearch', '8.0', 'Search and analytics engine', 'Databases');

-- Insert DevOps tools
INSERT INTO skills (name, version, description, category) VALUES
    ('Docker', 'latest', 'Container platform', 'DevOps'),
    ('Kubernetes', 'latest', 'Container orchestration', 'DevOps'),
    ('Git', 'latest', 'Version control system', 'DevOps'),
    ('Jenkins', 'latest', 'Continuous Integration server', 'DevOps'),
    ('AWS', 'latest', 'Cloud platform services', 'Cloud'),
    ('Azure', 'latest', 'Microsoft cloud platform', 'Cloud'),
    ('Terraform', 'latest', 'Infrastructure as Code tool', 'DevOps'),
    ('Ansible', 'latest', 'Automation platform', 'DevOps'),
    ('GraphQL', 'latest', 'API query language', 'APIs');

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

-- Insert user skills (emma_frontend)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 5, 4.0, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'emma_frontend' AND s.name IN ('TypeScript', 'React', 'NextJS', 'GraphQL');

-- Insert user skills (lisa_mobile)
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience, last_used_date)
SELECT u.id, s.id, 4, 3.0, CURRENT_DATE
FROM users u, skills s
WHERE u.username = 'lisa_mobile' AND s.name IN ('Swift', 'Kotlin', 'Flutter');

-- Insert example issues
INSERT INTO issues (skill_id, user_id, title, description, created_at, updated_at)
SELECT s.id, u.id, 'How to handle async operations in React?', 'I am having trouble handling async operations in React. Can someone help?', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'React' AND s.version = '18.0' AND u.username = 'john_dev';

INSERT INTO issues (skill_id, user_id, title, description, created_at, updated_at)
SELECT s.id, u.id, 'Best practices for Dockerfile', 'What are some best practices for writing Dockerfiles?', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'Docker' AND s.version = 'latest' AND u.username = 'mike_devops';

INSERT INTO issues (skill_id, user_id, title, description, created_at, updated_at)
SELECT s.id, u.id, 'Understanding Flutter state management', 'What are the best practices for state management in Flutter?', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'Flutter' AND u.username = 'lisa_mobile';

INSERT INTO issues (skill_id, user_id, title, description, created_at, updated_at)
SELECT s.id, u.id, 'NextJS vs Traditional React', 'What are the main advantages of using NextJS over traditional React?', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'NextJS' AND u.username = 'emma_frontend';

-- Insert example comments
INSERT INTO comments (issue_id, user_id, content, created_at)
SELECT i.id, u.id, 'You can use async/await to handle async operations in React.', NOW()
FROM issues i, users u
WHERE i.title = 'How to handle async operations in React?' AND u.username = 'maria_tech';

INSERT INTO comments (issue_id, user_id, content, created_at)
SELECT i.id, u.id, 'Make sure to minimize the number of layers in your Dockerfile.', NOW()
FROM issues i, users u
WHERE i.title = 'Best practices for Dockerfile' AND u.username = 'alex_data';

INSERT INTO comments (issue_id, user_id, content, created_at)
SELECT i.id, u.id, 'Provider and Riverpod are popular choices for Flutter state management.', NOW()
FROM issues i, users u
WHERE i.title = 'Understanding Flutter state management' AND u.username = 'david_backend';

INSERT INTO comments (issue_id, user_id, content, created_at)
SELECT i.id, u.id, 'NextJS provides built-in SSR and better performance out of the box.', NOW()
FROM issues i, users u
WHERE i.title = 'NextJS vs Traditional React' AND u.username = 'john_dev';

-- Insert example guides
INSERT INTO guides (skill_id, user_id, title, content, created_at, updated_at)
SELECT s.id, u.id, 'Getting Started with React', '# Getting Started with React\n\nReact is a JavaScript library for building user interfaces. To get started, you need to install React and create a new project...', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'React' AND s.version = '18.0' AND u.username = 'sara_web';

INSERT INTO guides (skill_id, user_id, title, content, created_at, updated_at)
SELECT s.id, u.id, 'Docker Basics', '# Docker Basics\n\nDocker is a platform for developing, shipping, and running applications. This guide will help you get started with Docker...', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'Docker' AND s.version = 'latest' AND u.username = 'mike_devops';

INSERT INTO guides (skill_id, user_id, title, content, created_at, updated_at)
SELECT s.id, u.id, 'Flutter State Management Guide', '# Flutter State Management\n\nState management is crucial in Flutter applications. This guide covers different approaches including Provider, Riverpod, and BLoC...', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'Flutter' AND u.username = 'lisa_mobile';

INSERT INTO guides (skill_id, user_id, title, content, created_at, updated_at)
SELECT s.id, u.id, 'NextJS Advanced Features', '# NextJS Advanced Features\n\nLearn about advanced NextJS features including API routes, ISR, middleware, and more...', NOW(), NOW()
FROM skills s, users u
WHERE s.name = 'NextJS' AND u.username = 'emma_frontend';


