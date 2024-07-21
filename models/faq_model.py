import ast
import json
import uuid
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor, register_uuid
from utils.config import get_config
import psycopg2

# Register UUID type
register_uuid()

class FAQModel:
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
    def insert_faq(faq_data):
        faq_id = uuid.uuid4()
        with FAQModel.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO tbl_faqs (id, doc_id, topic, question, answers, supporting_facts, 
                                          possible_user_intents, context, readability_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    faq_id,
                    faq_data['doc_id'],
                    faq_data['topic'],
                    faq_data['question'],
                    json.dumps(faq_data['answers']),
                    json.dumps(faq_data['supporting_facts']),
                    json.dumps(faq_data['possible_user_intents']),
                    faq_data['context'],
                    faq_data['readability_score']
                ))
                conn.commit()
        return faq_id

    @staticmethod
    def get_faqs_by_doc_id(doc_id):
        with FAQModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, question FROM tbl_faqs WHERE doc_id = %s", (doc_id,))
                return [{'faq_id': row['id'], 'question': row['question']} for row in cursor.fetchall()]

    @staticmethod
    def _parse_faq(faq):
        if faq:
            json_fields = ['answers', 'supporting_facts', 'possible_user_intents']
            for field in json_fields:
                if field in faq and faq[field]:
                    if isinstance(faq[field], str):
                        try:
                            faq[field] = json.loads(faq[field])
                        except json.JSONDecodeError:
                            try:
                                faq[field] = ast.literal_eval(faq[field])
                            except (SyntaxError, ValueError):
                                pass
        return faq

    @staticmethod
    def get_faq_by_id(faq_id):
        with FAQModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM tbl_faqs WHERE id = %s", (faq_id,))
                faq = cursor.fetchone()
                return FAQModel._parse_faq(dict(faq)) if faq else None

    @staticmethod
    def doc_exists_with_faqs(doc_name):
        with FAQModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute('''
                    SELECT COUNT(*) as count FROM tbl_faqs f
                    JOIN tbl_docs d ON f.doc_id = d.id
                    WHERE d.doc_name = %s
                ''', (doc_name,))
                return cursor.fetchone()['count'] > 0

    @staticmethod
    def get_all():
        with FAQModel.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM tbl_faqs")
                faqs = cursor.fetchall()
                return [FAQModel._parse_faq(dict(faq)) for faq in faqs]
