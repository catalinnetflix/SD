from queryParser import QueryParser
import time

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def format_timestamp(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


class SearchEngine:
    def __init__(self, db_manager, history_manager):
        self.db = db_manager
        self.parser = QueryParser()
        self.history_manager = history_manager

    def search(self, query, report_type="summary"):
        self.history_manager.record_query(query)
        content_query, path_query, query_terms = self.parser.parse(query)

        content_query_str = " & ".join([term for term, _ in content_query])
        path_query_str = " AND ".join([term for term, _ in path_query])

        results = self.db.search(content_query_str, path_query_str)
        if not results:
            return []

        scored_results = []
        for row in results:
            filepath, filename, file_content, extension, size, timestamp, score = row
            scored_results.append((score, filepath, filename, extension, file_content, size, timestamp))

        scored_results.sort(reverse=True, key=lambda x: x[0])

        web_results = []
        for score, filepath, filename, extension, file_content, size, timestamp in scored_results:
            formatted_size = format_size(size)
            formatted_date = format_timestamp(timestamp)
            summary = f"Score: {score} - {filename}"
            detail = (f"Score: {score} - {filename} ({filepath})\n"
                      f"Size: {formatted_size}\n"
                      f"Last modified: {formatted_date}\n"
                      f"Content: {file_content[:100]}...")
            web_results.append({
                'filename': filename,
                'filepath': filepath,
                'score': score,
                'size': formatted_size,
                'timestamp': formatted_date,
                'content': file_content[:100],
                'extension': extension,
                'summary': summary,
                'detail': detail,
            })

        return web_results
