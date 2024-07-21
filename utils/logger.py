import logging
import sys

def setup_logging():
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        stream=sys.stdout
    )

    # Suppress specific loggers
    for logger_name in ['werkzeug', 'sqlalchemy.engine']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

def get_logger(name):
    return logging.getLogger(name)

# Setup logging when this module is imported
setup_logging()
