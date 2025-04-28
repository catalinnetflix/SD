import psycopg2

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "cata",
    "host": "localhost",
    "port": "5432"
}


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
                timestamp REAL,
                score INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_files_content 
            ON files USING gin(to_tsvector('english', content))
        ''')
        self.conn.commit()

    def insert_or_update_file(self, meta):
        try:
            self.cursor.execute("SELECT timestamp FROM files WHERE filepath = %s", (meta.filepath,))
            result = self.cursor.fetchone()

            if result:
                if result[0] != meta.timestamp:
                    self.cursor.execute('''
                        UPDATE files
                        SET filename = %s, content = %s, extension = %s, size = %s, timestamp = %s, score = %s
                        WHERE filepath = %s
                    ''', (meta.filename, meta.content, meta.extension, meta.size, meta.timestamp, meta.score, meta.filepath))
            else:
                self.cursor.execute('''
                    INSERT INTO files (filepath, filename, content, extension, size, timestamp, score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (meta.filepath, meta.filename, meta.content, meta.extension, meta.size, meta.timestamp, meta.score))

            self.conn.commit()
        except Exception as e:
            print(f"DB error for {meta.filepath}: {e}")

    def remove_deleted_files(self, indexed_paths):
        self.cursor.execute("SELECT filepath FROM files")
        all_files = {row[0] for row in self.cursor.fetchall()}
        to_remove = all_files - indexed_paths

        for file in to_remove:
            self.cursor.execute("DELETE FROM files WHERE filepath = %s", (file,))
        if to_remove:
            print(f"Removed {len(to_remove)} deleted files.")
        self.conn.commit()

    def search(self, content_query=None, path_query=None):
        where_clauses = []
        params = []

        if content_query:
            where_clauses.append("to_tsvector('english', content) @@ to_tsquery(%s)")
            params.append(content_query + ":*")

        if path_query:
            path_conditions = []
            for term in path_query.split(" AND "):
                path_conditions.append("filepath ILIKE %s")
                params.append(f"%{term}%")
            where_clauses.append("(" + " AND ".join(path_conditions) + ")")

        sql = "SELECT filepath, filename, content, extension, size, timestamp, score FROM files"

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY score DESC"

        self.cursor.execute(sql, tuple(params))
        results = self.cursor.fetchall()

        processed_results = []
        for row in results:
            filepath, filename, content, extension, size, timestamp, score = row
            timestamp = float(timestamp)
            processed_results.append((filepath, filename, content, extension, size, timestamp, score))

        return processed_results

    def search_files(self, query, search_type):
        if search_type == 'filename':
            self.cursor.execute('''
                SELECT filepath, filename, content, extension, size, timestamp 
                FROM files WHERE filename ILIKE %s
            ''', ('%' + query + '%',))
        elif search_type == 'content':
            tsquery = query + ':*'
            self.cursor.execute('''
                SELECT filepath, filename, content, extension, size, timestamp,
                ts_rank_cd(to_tsvector('english', content), to_tsquery(%s)) as rank
                FROM files 
                WHERE to_tsvector('english', content) @@ to_tsquery(%s)
                ORDER BY rank DESC
            ''', (tsquery, tsquery))

        return self.cursor.fetchall()

    def get_file_timestamp(self, filepath):
        self.cursor.execute("SELECT timestamp FROM files WHERE filepath = %s", (filepath,))
        result = self.cursor.fetchone()
        if result:
            return float(result[0])
        return None

    def close(self):
        self.cursor.close()
        self.conn.close()