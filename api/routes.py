from flask import Blueprint
from .controllers import DocumentController, FAQController, EmbeddingController

bp = Blueprint('api', __name__)

@bp.route('/docs', methods=['GET'])
def get_all_docs():
    return DocumentController.get_all_docs()

@bp.route('/docs/<string:doc_id>/faqs', methods=['GET'])
def get_faqs_by_doc(doc_id):
    return DocumentController.get_faqs_by_doc(doc_id)

@bp.route('/faqs/<string:faq_id>/details', methods=['GET'])
def get_faq_details(faq_id):
    return FAQController.get_faq_details(faq_id)

@bp.route('/create', methods=['POST'])
def create_documents():
    return DocumentController.create_docs_faqs()

@bp.route('/embed', methods=['POST'])
def create_embeddings():
    return EmbeddingController.create_embeddings()
