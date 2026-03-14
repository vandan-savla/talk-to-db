from utils.connect import connect_to_db
from langchain_core.tools import tool

@tool("execute_sql_query", return_direct=True)
def execute_sql_query(sql_query: str, operation: str) -> list[dict]:
    """
    Execute the given SQL query and return the results as a list of dictionaries.
    """
    try:
        if operation.lower() != "select":
            raise ValueError("Only SELECT queries are allowed.")
         
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        dict_results = [dict(zip(columns, row)) for row in results]
        return dict_results
    
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        cursor.close()
        conn.close()