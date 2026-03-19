-- ============================================================
-- 01_init_app_db.sql
-- Creates application_db and all tables
-- Run as superuser: psql -U postgres -f 01_init_app_db.sql
-- ============================================================

-- Connect to it
\c application_db


-- ── Extensions ───────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);


-- ── Conversations ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id  TEXT UNIQUE NOT NULL,
    title      TEXT DEFAULT 'Untitled Conversation',
    created_at TIMESTAMP DEFAULT NOW()
);


-- ── Messages ──────────────────────────────────────────────────
-- Stores only two rows per conversation turn:
-- role='user'      → { "question": "..." }
-- role='assistant' → { "answer": "...", "sql_query": "..." }
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content         JSON NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);


-- ── Indexes ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_conversations_user_id   ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_thread_id  ON conversations(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at      ON messages(created_at);