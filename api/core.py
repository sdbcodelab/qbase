import dspy
from services.file_processor import FileProcessor
from services.context_processor import ContextAnalyzer
from models.doc_model import DocModel
from models.faq_model import FAQModel
from utils.logger import get_logger
from utils.config import get_config

logger = get_logger(__name__)

class OpenAILM(dspy.OpenAI):
    def __init__(self, api_key, model):
        super().__init__(api_key=api_key, model=model)

def get_lm():
    api_key = get_config('OPENAI_API_KEY')
    model = get_config('OPENAI_MODEL')
    return OpenAILM(api_key=api_key, model=model)

def process_documents():
    try:
        lm = get_lm()
        dspy.settings.configure(lm=lm)

        file_processor = FileProcessor()
        contexts = file_processor.get_contexts()

        if not contexts:
            logger.warning("No contexts found. Exiting.")
            return 0, 0

        analyzer = ContextAnalyzer()
        docs_processed = 0
        faqs_processed = 0

        for context_data in contexts:
            doc_name = context_data['file_name']
            logger.info(f"Processing file: {doc_name}")

            if FAQModel.doc_exists_with_faqs(doc_name):
                logger.info(f"Document '{doc_name}' already has FAQs. Skipping.")
                continue

            doc_id = DocModel.get_or_create_doc(doc_name)

            for section in context_data['sections']:
                context = section['content']
                topic = section['topic']

                logger.info(f"Analyzing section: {topic}")
                result = analyzer(context)

                if result['questions_answers']:
                    for qa in result['questions_answers']:
                        faq_data = {
                            'doc_id': doc_id,
                            'question': qa['question'],
                            'answers': {
                                'simple': qa.get('simple_answer', ''),
                                'short': qa.get('short_answer', ''),
                                'standard': qa.get('standard_answer', '')
                            },
                            'topic': result['topic'],
                            'supporting_facts': qa.get('supporting_facts', []),
                            'possible_user_intents': result.get('user_intents', []),
                            'readability_score': result.get('readability_score', 0),
                            'context': context
                        }
                        FAQModel.insert_faq(faq_data)
                        faqs_processed += 1
                else:
                    logger.warning(f"No questions generated for section: {topic}")

            docs_processed += 1

        logger.info(f"Analysis completed. Processed {docs_processed} new documents and {faqs_processed} FAQs.")
        return docs_processed, faqs_processed
    except Exception as e:
        logger.error(f"An error occurred during document processing: {e}")
        return 0, 0
