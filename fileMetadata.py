from pathlib import Path
from collections import Counter
import os
import datetime
from scoring import compute_score

TEXT_EXTENSIONS = {".txt", ".md", ".log", ".csv", ".json", ".pdf"}

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
        return compute_score(
            self.filepath,
            self.content,
            self.extension,
            self.size,
            self.timestamp,
            self.query_terms
        )

    @staticmethod
    def analyze_metadata(results):
        """
        Accepts a list of tuples: (filepath, filename, content, extension, size, timestamp, score)
        and returns a summary dict.
        """
        file_types = Counter()
        modified_years = Counter()
        languages = Counter()

        for row in results:
            if not isinstance(row, (tuple, list)) or len(row) < 7:
                continue

            filepath, filename, _, extension, _, timestamp, _ = row
            ext = extension.lower().strip('.')
            if ext:
                file_types[ext] += 1

            try:
                year = str(datetime.datetime.fromtimestamp(timestamp).year)
                modified_years[year] += 1
            except Exception:
                continue

            fname = filename.lower()
            if 'java' in fname:
                languages['Java'] += 1
            elif 'py' in fname:
                languages['Python'] += 1
            elif 'c' in fname:
                languages['C'] += 1

        return {
            "File Type": dict(file_types),
            "Modified Year": dict(modified_years),
            "Language": dict(languages)
        }
