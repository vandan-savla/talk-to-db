-- ── Create user ───────────────────────────────────────────────
CREATE USER app_user WITH PASSWORD 'admin';
 
 
-- ── Create database ───────────────────────────────────────────
CREATE DATABASE application_db;
 
 
-- ── Give ownership ────────────────────────────────────────────
ALTER DATABASE application_db OWNER TO app_user;
 
 
-- ── Connect to database ───────────────────────────────────────
\c application_db
 
 
-- ── Extensions ────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
 
 
-- ── Schema permissions ────────────────────────────────────────
GRANT ALL ON SCHEMA public TO app_user;
 
 
-- ── Future tables/sequences ───────────────────────────────────
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO app_user;
 
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO app_user;
 
