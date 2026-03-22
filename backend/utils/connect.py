import psycopg2
from psycopg2.extras import RealDictCursor
import os 
from dotenv import load_dotenv
load_dotenv()
def connect_to_master_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_MASTER_HOST") or "localhost",
            port=os.getenv("POSTGRES_MASTER_PORT"),
            user=os.getenv("POSTGRES_MASTER_USER") or "postgres",
            password=os.getenv("POSTGRES_MASTER_PASSWORD") or "admin",
            dbname=os.getenv("POSTGRES_MASTER_DB") or "postgres",
        )
        print("Connection to database established successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
    
def connect_to_app_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_APP_HOST") or "localhost",
            port=os.getenv("POSTGRES_APP_PORT"),
            user=os.getenv("POSTGRES_APP_USER") or "app_user",
            password=os.getenv("POSTGRES_APP_PASSWORD") or "admin",
            dbname=os.getenv("POSTGRES_APP_DB") or "application_db",
            cursor_factory=RealDictCursor
        )
        print("Connection to app database established successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to app database: {e}")
        return None