from langchain_core.documents import Document


def build_schema_documents(db_structure) -> list[Document]:

    documents = []

    for schema, tables in db_structure.items():

        for table_name, table_data in tables.items():

            columns = table_data["columns"]
            description = table_data["table_description"]

            column_text = []

            for col in columns:
                column_text.append(
                    f"{col['name']} ({col['type']}): {col['description']}"
                )

            schema_text = f"""
                Table: {table_name}

                Description:
                {description}

                Columns:
                {" ".join(column_text)}
            """

            doc = Document(
                page_content=schema_text,
                metadata={
                    "schema": schema,
                    "table_name": table_name,
                    "table_description": description,
                    "columns": columns
                }
            )

            documents.append(doc)

    return documents