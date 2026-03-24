import logging
from utils.connect import connect_to_master_db

logger = logging.getLogger(__name__)

def execute_sql_query(sql_query: str) -> list[dict]:
    conn = None
    cursor = None
    try:
        logger.info(f"Executing SQL: {sql_query[:100]}...")
        
        if not sql_query.strip().lower().startswith("select"):
            logger.warning("Attempted non-SELECT query.")
            return [{"error": "Only SELECT queries are permitted."}]

        conn = connect_to_master_db()
        if not conn:
            logger.error("Failed to connect to master database.")
            return [{"error": "Internal database connection error."}]
            
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        logger.info(f"Query returned {len(results)} rows.")
        return [dict(zip(columns, row)) for row in results]

    except Exception as e:
        logger.error(f"SQL Execution error: {e}", exc_info=True)
        return [{"error": "Query execution failed. Please try a different question."}]

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()