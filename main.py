import os
import psycopg2
from pathlib import Path

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "cata",
    "host": "localhost",
    "port": "5432"
}

TEXT_EXTENSIONS = {".txt", ".md", ".log", ".csv", ".json"}


class DatabaseManager:
    
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                filepath TEXT UNIQUE,
                filename TEXT,
                content TEXT,
                extension TEXT,
                size INTEGER,
                timestamp REAL
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_files_content 
            ON files USING gin(to_tsvector('english', content))
        ''')
        self.conn.commit()

    def insert_or_update_file(self, filepath, filename, content, extension, size, timestamp):
        try:
            self.cursor.execute("SELECT timestamp FROM files WHERE filepath = %s", (filepath,))
            result = self.cursor.fetchone()

            if result:
                stored_timestamp = result[0]
                if stored_timestamp != timestamp:
                    self.cursor.execute('''
                        UPDATE files
                        SET filename = %s, content = %s, extension = %s, size = %s, timestamp = %s
                        WHERE filepath = %s
                    ''', (filename, content, extension, size, timestamp, filepath))
            else:
                self.cursor.execute('''
                    INSERT INTO files (filepath, filename, content, extension, size, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (filepath, filename, content, extension, size, timestamp))

            self.conn.commit()
        except Exception as e:
            print(f"Error inserting or updating {filepath}: {e}")

    def remove_deleted_files(self, indexed_files):
        try:
            self.cursor.execute("SELECT filepath FROM files")
            stored_files = {row[0] for row in self.cursor.fetchall()}

            files_to_remove = stored_files - indexed_files

            if files_to_remove:
                for file in files_to_remove:
                    self.cursor.execute("DELETE FROM files WHERE filepath = %s", (file,))
                self.conn.commit()
                print(f"Removed {len(files_to_remove)} missing files from the database.")
        except Exception as e:
            print(f"Error removing deleted files: {e}")

    def search_files(self, query, search_type):
        if search_type == 'filename':
            self.cursor.execute('''
                SELECT filepath, filename, extension, content FROM files
                WHERE filename ILIKE %s
                ORDER BY filename
            ''', ('%' + query + '%',))
        elif search_type == 'content':
             query = query + ':*'  
             self.cursor.execute('''
        SELECT filepath, filename, extension, content FROM files
        WHERE to_tsvector('english', content) @@ to_tsquery(%s)
        ORDER BY ts_rank_cd(to_tsvector('english', content), to_tsquery(%s)) DESC
    ''', (query, query))
    
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


class FileIndexer:
    
    def __init__(self, root_dir, db_manager):
        self.root_dir = root_dir
        self.db_manager = db_manager

    def get_file_metadata(self, filepath):
        try:
            extension = os.path.splitext(filepath)[1].lower()
            size = os.path.getsize(filepath)
            timestamp = os.path.getmtime(filepath)
            return extension, size, timestamp
        except Exception as e:
            print(f"Error getting metadata for {filepath}: {e}")
            return None, None, None

    def extract_text_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception:
            return "(NOT GOOD)"

    def crawl_and_index(self):
        indexed_files = set()

        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                indexed_files.add(filepath)

                extension, size, timestamp = self.get_file_metadata(filepath)

                if extension is None:
                    continue  

                content = self.extract_text_content(filepath) if extension in TEXT_EXTENSIONS else "(Binary or non-text file)"
                
                self.db_manager.insert_or_update_file(filepath, filename, content, extension, size, timestamp)

        self.db_manager.remove_deleted_files(indexed_files)
        print("Indexing completed.")


class SearchEngine:
    
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def search(self, query, search_type):
        results = self.db_manager.search_files(query, search_type)
    
        if not results:
            print("No results found.")
        else:
            print(f"\nFound {len(results)} results:")
            for filepath, filename, extension, content in results:
                print(f"\nFile: {filename}\nPath: {filepath}")
                if extension in TEXT_EXTENSIONS:
                    print(f"Preview: {content[:500]}...")  
                else:
                    print("(NOT GOOD)")
                print("-" * 50)


class FileSearchApp:
    
    def __init__(self, root_dir):
        self.db_manager = DatabaseManager()
        self.file_indexer = FileIndexer(root_dir, self.db_manager)
        self.search_engine = SearchEngine(self.db_manager)

    def run(self):
        if not os.path.exists(self.file_indexer.root_dir):
            os.makedirs(self.file_indexer.root_dir)
            print(f"Created {self.file_indexer.root_dir}. Please add some files and rerun.")
            return

        print(f"Indexing files in {self.file_indexer.root_dir}...")
        self.file_indexer.crawl_and_index()

        while True:
            search_type = input("\nChoose search type (1 for filename, 2 for content, 'quit' to exit): ").strip().lower()
            if search_type == 'quit':
                self.db_manager.close()
                break

            if search_type == '1':
                query = input("Enter filename query: ").strip()
                self.search_engine.search(query, search_type='filename')
            elif search_type == '2':
                query = input("Enter search word for content: ").strip()
                self.search_engine.search(query, search_type='content')
            else:
                print("Invalid choice. Please choose '1' for filename or '2' for content.")
                continue


if __name__ == "__main__":
    root_directory = "C:/Users/Cata/Desktop/sdProject/test_files"
    app = FileSearchApp(root_directory)
    app.run()
