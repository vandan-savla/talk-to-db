import psycopg2
from psycopg2.extras import RealDictCursor
import os 
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def connect_to_master_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST") or "localhost",
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_MASTER_USER") ,
            password=os.getenv("POSTGRES_MASTER_PASSWORD"),
            dbname=os.getenv("POSTGRES_MASTER_DB") or "postgres",
        )
        logger.info("Connection to master database established successfully.")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to master database: {e}", exc_info=True)
        return None
    
def connect_to_app_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST") or "localhost",
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_APP_USER") ,
            password=os.getenv("POSTGRES_APP_PASSWORD"),
            dbname=os.getenv("POSTGRES_APP_DB") or "application_db",
            cursor_factory=RealDictCursor
        )
        logger.info("Connection to app database established successfully.")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to app database: {e}", exc_info=True)
        return None