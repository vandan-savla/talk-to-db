from langchain_core.documents import Document


def build_schema_documents(db_structure) -> list[Document]:

    documents = []

    for schema, tables in db_structure.items():

        for table_name, table_data in tables.items():

            columns = table_data["columns"]
            description = table_data.get("table_description", "No description")
            relationships = table_data.get("relationships", [])

            # -------------------
            # COLUMN TEXT
            # -------------------
            column_lines = []

            for col in columns:
                column_lines.append(
                    f"{col['name']} ({col['type']}): {col['description']}"
                )

            # -------------------
            # RELATIONSHIP TEXT
            # -------------------
            relationship_lines = []

            for rel in relationships:
                relationship_lines.append(
                    f"{table_name}.{rel['column']} -> "
                    f"{rel['references_table']}.{rel['references_column']}"
                )

            # -------------------
            # FINAL EMBEDDING TEXT
            # -------------------
            schema_text = f"""
                Table: {table_name}

                Description:
                {description}

                Columns:
                {" ".join(column_lines)}

                Relationships:
                {" ".join(relationship_lines) if relationship_lines else "None"}
                """.strip()

            doc = Document(
                page_content=schema_text,
                metadata={
                    "schema": schema,
                    "table_name": table_name,
                    "table_description": description,
                    "columns": columns,
                    "relationships": relationships
                }
            )

            documents.append(doc)

    return documents