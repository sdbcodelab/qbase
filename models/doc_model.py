import uuid
from datetime import datetime
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor, register_uuid
from utils.config import get_config
import psycopg2

# Register UUID type
register_uuid()

class DocModel:
    @staticmethod
    @contextmanager
    def get_db_connection():
        conn = psycopg2.connect(
            dbname=get_config('DB_NAME'),
            user=get_config('DB_USER'),
            password=get_config('DB_PASSWORD'),
            host=get_config('DB_HOST'),
            port=get_config('DB_PORT')
        )
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def get_or_create_doc(doc_name):
        with DocModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id FROM tbl_docs WHERE doc_name = %s", (doc_name,))
                result = cursor.fetchone()
                
                if result:
                    doc_id = result['id']
                else:
                    doc_id = uuid.uuid4()
                    cursor.execute('''
                        INSERT INTO tbl_docs (id, doc_name, is_active, created_on)
                        VALUES (%s, %s, %s, %s)
                    ''', (doc_id, doc_name, True, datetime.now()))
                    conn.commit()
            
        return doc_id

    @staticmethod
    def get_name_by_id(doc_id):
        with DocModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT doc_name FROM tbl_docs WHERE id = %s", (doc_id,))
                result = cursor.fetchone()
        return result['doc_name'] if result else None

    @staticmethod
    def get_all():
        with DocModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, doc_name, is_active, created_on FROM tbl_docs")
                docs = cursor.fetchall()
        return docs