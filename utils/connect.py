import psycopg2
from psycopg2 import sql
import os 
from dotenv import load_dotenv
load_dotenv()
def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        )
        print("Connection to database established successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
    