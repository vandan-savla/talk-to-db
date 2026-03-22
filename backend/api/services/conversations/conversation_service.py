import json
from typing import Optional
from utils.connect import connect_to_app_db


# ── Create a new conversation ─────────────────────────────────
def create_conversation(user_id: str, title: str) -> dict:
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (user_id, title)
                VALUES (%s, %s)
                RETURNING id, user_id, title, created_at
                """,
                (user_id, title)
            )
            row = dict(cur.fetchone())
            conn.commit()
        return {
            "id": str(row["id"]),   # use this as thread_id in /v1/query
            "title": row["title"],
            "created_at": row["created_at"].isoformat()
        }
    except Exception as e:
        conn.rollback()
        print(f"[create_conversation] Error: {e}")
        raise
    finally:
        conn.close()


# ── Get all conversations for a user ─────────────────────────
def get_conversations(user_id: str) -> list[dict]:
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, created_at
                FROM conversations
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            rows = cur.fetchall()
        return [
            {
                "id": str(r["id"]),
                "title": r["title"],
                "created_at": r["created_at"].isoformat()
            }
            for r in rows
        ]
    finally:
        conn.close()

# ── Get a single conversation by id ──────────────────────────
def get_conversation_by_id(conversation_id: str) -> Optional[dict]:
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, user_id, title FROM conversations WHERE id = %s",
                (conversation_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


# ── Update conversation title from first user message ─────────
def update_conversation_title(conversation_id: str, title: str):
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE conversations SET title = %s WHERE id = %s",
                (title[:100], conversation_id)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[update_conversation_title] Error: {e}")
    finally:
        conn.close()


# ── Save user + assistant message pair ────────────────────────
def save_messages(conversation_id: str, user_question: str, answer: str, sql_query: str = ""):
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, 'user', %s)
                """,
                (conversation_id, json.dumps({"question": user_question}))
            )
            cur.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, 'assistant', %s)
                """,
                (conversation_id, json.dumps({"answer": answer, "sql_query": sql_query}))
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[save_messages] Error: {e}")
    finally:
        conn.close()


# ── Get all messages for a conversation ───────────────────────
def get_messages(conversation_id: str) -> list[dict]:
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, role, content, created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            rows = cur.fetchall()
        return [
            {
                "id": str(r["id"]),
                "role": r["role"],
                "content": r["content"],
                "created_at": r["created_at"].isoformat()
            }
            for r in rows
        ]
    finally:
        conn.close()


# ── Delete a conversation ────────────────────────────────────
def delete_conversation(conversation_id: str):
    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            # Delete messages first (if not handled by CASCADE)
            cur.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
            # Delete conversation
            cur.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[delete_conversation] Error: {e}")
        raise
    finally:
        conn.close()
