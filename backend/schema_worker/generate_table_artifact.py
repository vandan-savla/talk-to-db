from datetime import datetime
import os
import json
from utils.connect import connect_to_master_db


def generate_table_artifacts(version=None):

    if version is None:
        version = datetime.now().strftime("%Y_%m_%d_%H_%M")

    connection = connect_to_master_db()
    cursor = connection.cursor()

    column_query = """
    SELECT 
        cols.table_schema, 
        cols.table_name, 
        cols.column_name, 
        cols.data_type,
        pg_catalog.col_description(c.oid, cols.ordinal_position::int) AS column_description,
        pg_catalog.obj_description(c.oid, 'pg_class') AS table_description
    FROM information_schema.columns cols
    JOIN pg_class c ON c.relname = cols.table_name
    JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = cols.table_schema
    WHERE cols.table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY cols.table_schema, cols.table_name, cols.ordinal_position;
    """

    fk_query = """
    SELECT
        tc.table_schema,
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('information_schema', 'pg_catalog');
    """

    try:
        cursor.execute(column_query)
        rows = cursor.fetchall()

        db_structure = {}

        for schema, table, col, dtype, col_desc, tab_desc in rows:

            if schema not in db_structure:
                db_structure[schema] = {}

            if table not in db_structure[schema]:
                db_structure[schema][table] = {
                    "table_name": table,
                    "table_description": tab_desc or "No description",
                    "columns": [],
                    "relationships": []
                }

            db_structure[schema][table]["columns"].append({
                "name": col,
                "type": dtype,
                "description": col_desc or "No description"
            })

        cursor.execute(fk_query)
        fk_rows = cursor.fetchall()

        for schema, table, column, ref_table, ref_column in fk_rows:

            if schema in db_structure and table in db_structure[schema]:

                db_structure[schema][table]["relationships"].append({
                    "column": column,
                    "references_table": ref_table,
                    "references_column": ref_column
                })

        for schema, tables in db_structure.items():
            for table_name, data in tables.items():

                folder_path = os.path.join(".artifacts", schema, table_name)
                os.makedirs(folder_path, exist_ok=True)

                file_path = os.path.join(folder_path, f"artifact_{version}.json")

                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)

        print(f"Artifacts successfully generated for {len(db_structure)} schemas.")
        return db_structure

    except Exception as e:
        print(f"Error generating artifacts: {e}")

    finally:
        cursor.close()