from datetime import datetime
import os
import json
from utils.connect import connect_to_db

def generate_table_artifacts(version=None):
    """
    Fetches comprehensive metadata and saves it into a versioned folder structure.
    Path: .artifacts/<schema>/<table_name>/artifact_<version>.json
    """

    if version is None:
        version = datetime.now().strftime("%Y_%m_%d_%H_%M")
    
    connection = connect_to_db()

    cursor = connection.cursor()
    
    # Query to get Table + Column + Data Type + Descriptions
    query = """
    SELECT 
        cols.table_schema, 
        cols.table_name, 
        cols.column_name, 
        cols.data_type,
        pg_catalog.col_description(c.oid, cols.ordinal_position::int) AS column_description,
        pg_catalog.obj_description(c.oid, 'pg_class') AS table_description
    FROM 
        information_schema.columns cols
    JOIN 
        pg_class c ON c.relname = cols.table_name
    JOIN 
        pg_namespace n ON n.oid = c.relnamespace AND n.nspname = cols.table_schema
    WHERE 
        cols.table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY 
        cols.table_schema, cols.table_name, cols.ordinal_position;
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        # Organize data by Schema -> Table
        db_structure = {}
        for schema, table, col, dtype, col_desc, tab_desc in rows:
            if schema not in db_structure:
                db_structure[schema] = {}
            if table not in db_structure[schema]:
                db_structure[schema][table] = {
                    "table_name": table,
                    "table_description": tab_desc or "No description",
                    "columns": []
                }
            
            db_structure[schema][table]["columns"].append({
                "name": col,
                "type": dtype,
                "description": col_desc or "No description"
            })

        # Create the .artifacts directory structure
        for schema, tables in db_structure.items():
            for table_name, data in tables.items():
                # Path: .artifacts/public/users/
                folder_path = os.path.join(".artifacts", schema, table_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Filename: artifact_v1.json
                file_path = os.path.join(folder_path, f"artifact_{version}.json")
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
        print(f"Artifacts successfully generated for {len(db_structure)} schemas.")
        return db_structure

    except Exception as e:
        print(f"Error generating artifacts: {e}")
    finally:
        cursor.close()

generate_table_artifacts()