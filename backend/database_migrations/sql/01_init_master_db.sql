-- Create user
-- CREATE USER postgres WITH PASSWORD 'admin';

-- Create database
CREATE DATABASE master_db;

-- Give ownership
ALTER DATABASE master_db OWNER TO primary_backend_data_user;

-- Connect to DB
\c master_db;

-- Schema permissions
GRANT ALL ON SCHEMA public TO primary_backend_data_user;

-- Future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO primary_backend_data_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT ALL ON SEQUENCES TO primary_backend_data_user;