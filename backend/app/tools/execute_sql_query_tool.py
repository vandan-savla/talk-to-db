from utils.connect import connect_to_db

def execute_sql_query(sql_query: str) -> list[dict]:
    conn = None
    cursor = None
    try:
        # Security check before touching DB
        stripped = sql_query.strip().upper()
        if not stripped.startswith("SELECT"):
            return [{"error": "Only SELECT queries are permitted."}]

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results]

    except Exception as e:
        print(f"[execute_sql_query] Internal error: {e}")  # log internally only
        return [{"error": "Query execution failed. Please try a different question."}]

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()