import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
import uuid
from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)

# Register UUID type
register_uuid()

class Database:
    @staticmethod
    def get_connection():
        try:
            conn = psycopg2.connect(
                dbname=get_config('DB_NAME'),
                user=get_config('DB_USER'),
                password=get_config('DB_PASSWORD'),
                host=get_config('DB_HOST'),
                port=get_config('DB_PORT')
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    @staticmethod
    def execute_query(query, params=None, fetch=True):
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                conn.commit()
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def table_exists(table_name):
        query = "SELECT to_regclass(%s) IS NOT NULL AS exists"
        result = Database.execute_query(query, (table_name,))
        return result[0]['exists']

    @staticmethod
    def create_tables():
        tables = {
            'tbl_docs': '''
                CREATE TABLE IF NOT EXISTS tbl_docs (
                    id UUID PRIMARY KEY,
                    doc_name TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    created_on TIMESTAMP NOT NULL
                )
            ''',
            'tbl_faqs': '''
                CREATE TABLE IF NOT EXISTS tbl_faqs (
                    id UUID PRIMARY KEY,
                    doc_id UUID NOT NULL,
                    topic TEXT,
                    question TEXT NOT NULL,
                    answers JSONB,
                    supporting_facts JSONB,
                    possible_user_intents JSONB,
                    context TEXT,
                    readability_score REAL,
                    FOREIGN KEY (doc_id) REFERENCES tbl_docs (id)
                )
            ''',
            'tbl_docs_v': '''
                CREATE TABLE IF NOT EXISTS tbl_docs_v (
                    id UUID PRIMARY KEY,
                    doc_name_v vector(1536)
                )
            ''',
            'tbl_faqs_v': '''
                CREATE TABLE IF NOT EXISTS tbl_faqs_v (
                    id UUID PRIMARY KEY,
                    topic_v vector(1536),
                    question_v vector(1536),
                    possible_user_intents_v vector(1536)
                )
            '''
        }
        
        for table_name, query in tables.items():
            if not Database.table_exists(table_name):
                logger.info(f"Creating table: {table_name}")
                Database.execute_query(query, fetch=False)
            else:
                logger.info(f"Table {table_name} already exists")

def initialize_database():
    logger.info("Initializing database...")
    try:
        Database.create_tables()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
