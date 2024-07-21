from utils.logger import get_logger
from api import create_app
from models.setup import Database

logger = get_logger(__name__)

def initialize_app():
    logger.info("Initializing the application...")
    
    # Create tables
    Database.create_tables()
    logger.info("Database tables created.")

if __name__ == '__main__':
    initialize_app()
    
    app = create_app()
    logger.info("Starting the API server...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
