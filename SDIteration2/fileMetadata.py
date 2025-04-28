from pathlib import Path
import os
from scoring import compute_score

TEXT_EXTENSIONS = {".txt", ".md", ".log", ".csv", ".json", ".pdf", ".docx"}

class FileMetadata:
    def __init__(self, filepath, query_terms=None):
        self.filepath = filepath
        self.path_obj = Path(filepath)
        self.filename = self.path_obj.name
        self.extension = self.path_obj.suffix.lower()
        self.size = os.path.getsize(filepath)
        self.timestamp = os.path.getmtime(filepath)
        self.content = self.extract_text_content() if self.extension in TEXT_EXTENSIONS else "(Binary or non-text file)"
        self.query_terms = query_terms

        self.score = self.compute_score()

    def extract_text_content(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return "(ERROR READING FILE)"

    def compute_score(self):
        return compute_score(self.filepath, self.content, self.extension, self.size, self.timestamp, self.query_terms)
