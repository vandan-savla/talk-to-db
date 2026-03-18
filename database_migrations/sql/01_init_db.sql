-- Create user
CREATE USER postgres WITH PASSWORD 'admin';

-- Create database
CREATE DATABASE postgres;

-- Give ownership
ALTER DATABASE postgres OWNER TO postgres;

-- Connect to DB
\c postgres;

-- Schema permissions
GRANT ALL ON SCHEMA public TO postgres;

-- Future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO postgres;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO postgres;