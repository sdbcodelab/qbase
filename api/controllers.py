from flask import jsonify
from models.doc_model import DocModel
from models.faq_model import FAQModel
from models.embedding_model import EmbeddingModel
from .core import process_documents

class DocumentController:
    @staticmethod
    def create_docs_faqs():
        docs_processed, faqs_processed = process_documents()
        return jsonify({
            "message": "Files processed successfully",
            "docs_processed": docs_processed,
            "faqs_processed": faqs_processed
        })

    @staticmethod
    def get_all_docs():
        docs = DocModel.get_all()
        return jsonify(docs)

    @staticmethod
    def get_faqs_by_doc(doc_id):
        faqs = FAQModel.get_faqs_by_doc_id(doc_id)
        doc_name = DocModel.get_name_by_id(doc_id)
        return jsonify({
            "doc_name": doc_name,
            "faqs": [{"faq_id": faq['faq_id'], "question": faq['question']} for faq in faqs]
        })

class FAQController:
    @staticmethod
    def get_faq_details(faq_id):
        faq = FAQModel.get_faq_by_id(faq_id)
        if not faq:
            return jsonify({"error": "FAQ not found"}), 404
        doc_name = DocModel.get_name_by_id(faq['doc_id'])
        return jsonify({"doc_name": doc_name, "faq": faq})
    
class EmbeddingController:
    @staticmethod
    def create_embeddings():
        docs_embedded = EmbeddingModel.create_doc_embeddings()
        faqs_embedded = EmbeddingModel.create_faq_embeddings()
        return jsonify({
            "message": "Embeddings created successfully",
            "docs_embedded": docs_embedded,
            "faqs_embedded": faqs_embedded
        })
