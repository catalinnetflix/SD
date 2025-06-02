import os
from fileMetadata import FileMetadata
class FileIndexer:
    def __init__(self, root_dir, db_manager, query_terms=None):
        self.root = root_dir
        self.db = db_manager
        self.query_terms = query_terms if query_terms is not None else []

    def index(self):
        indexed_paths = set()
        for dirpath, _, files in os.walk(self.root):
            for file in files:
                full_path = os.path.join(dirpath, file)
                if not os.path.isfile(full_path):
                    continue
                try:
                    meta = FileMetadata(full_path, query_terms=self.query_terms)
                    self.db.insert_or_update_file(meta)
                    indexed_paths.add(full_path)
                except Exception as e:
                    print(f"Error indexing {full_path}: {str(e)} ({type(e)})")

        self.db.remove_deleted_files(indexed_paths)
        print("Indexing complete.")
