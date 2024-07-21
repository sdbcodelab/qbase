import os
import glob
import re
from utils.logger import get_logger
from utils.config import get_config

class FileProcessor:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.input_folder = self._get_absolute_path(get_config('DUMPED_FILES_PATH'))
        self.logger.info(f"FileProcessor initialized with input folder: {self.input_folder}")

    def _get_absolute_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', path))

    def read_markdown_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            pattern = r'^(#{1,2})\s+(.*?)$(.*?)(?=^#{1,2}\s|\Z)'
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

            sections = [
                {
                    'level': len(match.group(1)),
                    'topic': match.group(2).strip(),
                    'content': match.group(3).strip()
                }
                for match in matches
            ]

            self.logger.info(f"Read {len(sections)} sections from {file_path}")
            return sections
        except Exception as e:
            self.logger.error(f"Error reading markdown file {file_path}: {str(e)}")
            return []

    def get_contexts(self):
        self.logger.info("Starting context extraction from markdown files")
        contexts = []

        if not os.path.exists(self.input_folder):
            self.logger.error(f"Input folder does not exist: {self.input_folder}")
            return contexts

        md_files = glob.glob(os.path.join(self.input_folder, '**', '*.md'), recursive=True)
        self.logger.info(f"Found {len(md_files)} markdown files")

        if not md_files:
            self.logger.warning(f"No markdown files found in {self.input_folder}")
            return contexts

        for md_file in md_files:
            try:
                self.logger.info(f"Processing file: {md_file}")
                sections = self.read_markdown_file(md_file)
                if not sections:
                    self.logger.warning(f"No sections found in {md_file}. Skipping.")
                    continue

                file_context = {
                    'file_name': os.path.basename(md_file),
                    'sections': sections
                }
                contexts.append(file_context)
                self.logger.info(f"Added context for {file_context['file_name']} with {len(sections)} sections")
            except Exception as e:
                self.logger.error(f"Error processing file {md_file}: {str(e)}")

        self.logger.info(f"Context extraction completed. Processed {len(contexts)} files.")
        return contexts

def get_contexts():
    file_processor = FileProcessor()
    return file_processor.get_contexts()
