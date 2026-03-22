import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = f"postgresql://{os.getenv('POSTGRES_MASTER_USER')}:{os.getenv('POSTGRES_MASTER_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/master_db"
# DB_URL = os.getenv("POSTGRES_MASTER_DB_URL")

DATA_DIR = "./database_migrations/data"

engine = create_engine(DB_URL)

TABLE_ORDER = [
    "users",
    "products",
    "orders",
    "order_items"
]

def load_table(table):
    path = f"{DATA_DIR}/{table}.csv"
    if not os.path.exists(path):
        print(f"Skipping {table}, no CSV found")
        return

    df = pd.read_csv(path)

    print(f"Inserting into {table} ({len(df)} rows)")

    df.to_sql(
        table,
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )


if __name__ == "__main__":
    for table in TABLE_ORDER:
        load_table(table)