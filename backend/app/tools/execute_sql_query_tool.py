import logging
from utils.connect import connect_to_master_db

logger = logging.getLogger(__name__)
def execute_sql_query(sql_query: list[str] | str) -> list[dict]:
    conn = None
    cursor = None
    final_results = []

    try:
        # Ensure list
        if isinstance(sql_query, str):
            sql_query = [sql_query]

        conn = connect_to_master_db()
        if not conn:
            return [{"error": "Internal database connection error."}]

        cursor = conn.cursor()

        for sql in sql_query:
            logger.info(f"Executing SQL: {sql[:100]}...")

            if not sql.strip().lower().startswith("select"):
                logger.warning("Non-SELECT query blocked.")
                final_results.append({
                    "query": sql,
                    "error": "Only SELECT queries are permitted."
                })
                continue

            cursor.execute(sql)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = [dict(zip(columns, row)) for row in rows]

            final_results.extend(result)

        return final_results

    except Exception as e:
        logger.error(f"SQL Execution error: {e}", exc_info=True)
        return [{"error": "Query execution failed."}]

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
