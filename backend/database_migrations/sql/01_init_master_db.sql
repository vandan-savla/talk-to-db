-- Create user
-- CREATE USER postgres WITH PASSWORD 'admin';
CREATE USER master_user with PASSWORD 'admin';
-- Create database
CREATE DATABASE master_db;

-- Give ownership
ALTER DATABASE master_db OWNER TO master_user;

-- Connect to DB
\c master_db;

-- Schema permissions
GRANT ALL ON SCHEMA public TO master_user;

-- Future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO master_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT ALL ON SEQUENCES TO master_user;