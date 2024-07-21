import openai
from psycopg2.extras import execute_values
from .doc_model import DocModel
from .faq_model import FAQModel
from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingModel:
    def __init__(self):
        self.use_groq = get_config('USE_GROQ').lower() == 'true'
        if not self.use_groq:
            openai.api_key = get_config('OPENAI_API_KEY')
            self.client = openai.OpenAI()

    def create_embedding(self, text):
        try:
            if self.use_groq:
                # Implement Groq embedding if needed
                pass
            else:
                response = self.client.embeddings.create(
                    model=get_config('TEXT_MODEL'),
                    input=[text]
                )
                return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None

    @staticmethod
    def create_doc_embeddings():
        embedding_model = EmbeddingModel()
        docs = DocModel.get_all()
        embeddings = []
        for doc in docs:
            embedding = embedding_model.create_embedding(doc['doc_name'])
            if embedding:
                embeddings.append((doc['id'], embedding))

        with DocModel.get_db_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor,
                    "INSERT INTO tbl_docs_v (id, doc_name_v) VALUES %s ON CONFLICT (id) DO UPDATE SET doc_name_v = EXCLUDED.doc_name_v",
                    embeddings
                )
                conn.commit()
        
        return len(embeddings)

    @staticmethod
    def create_faq_embeddings():
        embedding_model = EmbeddingModel()
        faqs = FAQModel.get_all()
        embeddings = []
        for faq in faqs:
            topic_embedding = embedding_model.create_embedding(faq['topic'])
            question_embedding = embedding_model.create_embedding(faq['question'])
            intents_embedding = embedding_model.create_embedding(' '.join(faq['possible_user_intents']))
            if topic_embedding and question_embedding and intents_embedding:
                embeddings.append((faq['id'], topic_embedding, question_embedding, intents_embedding))

        with FAQModel.get_db_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor,
                    """
                    INSERT INTO tbl_faqs_v (id, topic_v, question_v, possible_user_intents_v) 
                    VALUES %s 
                    ON CONFLICT (id) DO UPDATE SET 
                        topic_v = EXCLUDED.topic_v,
                        question_v = EXCLUDED.question_v,
                        possible_user_intents_v = EXCLUDED.possible_user_intents_v
                    """,
                    embeddings
                )
                conn.commit()
        
        return len(embeddings)
