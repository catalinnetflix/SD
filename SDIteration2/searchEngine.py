from queryParser import QueryParser
from scoring import compute_score
import os
import json
import time

class SearchEngine:
    def __init__(self, db_manager, history_manager, report_format="detailed", cache_file="search_cache.json"):
        self.db = db_manager
        self.parser = QueryParser()
        self.history_manager = history_manager
        self.report_format = report_format
        self.cache_file = cache_file
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def format_timestamp(self, timestamp):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    def search(self, query, report_format="detailed"):
        self.report_format = report_format
        self.history_manager.record_query(query)

        content, path, query_terms = self.parser.parse(query)
        most_popular_suggestion = self.history_manager.suggest_most_popular_query(query)

        if most_popular_suggestion and most_popular_suggestion != query:
            print(f"Did you mean '{most_popular_suggestion}'? (Y/N)")
            user_input = input().strip().lower()
            if user_input == 'y':
                query = most_popular_suggestion
                content, path, query_terms = self.parser.parse(query)

        from_cache = False
        if query in self.cache:
            print("Checking cache for freshness...")
            cached_results = self.cache[query]
            cache_is_fresh = True

            for cached_result in cached_results:
                filepath = cached_result[1]
                current_timestamp = self.db.get_file_timestamp(filepath)

                if current_timestamp != cached_result[6]:
                    cache_is_fresh = False
                    break

            if cache_is_fresh:
                results = cached_results
                from_cache = True
                print(f"Results from cache.")
            else:
                print("Cache is outdated. Performing a fresh search...")
                results = self.db.search(content_query=content, path_query=path)
                self.cache[query] = results
                self.save_cache()
                from_cache = False
        else:
            print("Search performed through fresh search...")
            results = self.db.search(content_query=content, path_query=path)
            self.cache[query] = results
            self.save_cache()
            from_cache = False

        if not results:
            print("No results found.")
            return

        scored_results = []
        query_popularity = self.history_manager.query_popularity(query)

        for row in results:
            filepath, filename, content, extension, size, timestamp = row[:6]
            base_score = compute_score(filepath, content, extension, size, timestamp, query_terms)
            final_score = base_score
            scored_results.append((final_score, filepath, filename, extension, content, size, timestamp))

        scored_results.sort(reverse=True, key=lambda x: x[0])

        if self.report_format == "summary":
            print("\nAll results (Summary):")
            for score, filepath, filename, extension, content, size, timestamp in scored_results:
                print(f"Score: {score} - {filename} ({filepath})")
        elif self.report_format == "detailed":
            print("\nAll results (Detailed):")
            for score, filepath, filename, extension, content, size, timestamp in scored_results:
                formatted_size = self.format_size(size)
                formatted_date = self.format_timestamp(timestamp)
                print(f"Score: {score} - {filename} ({filepath})")
                print(f"Size: {formatted_size}")
                print(f"Last modified: {formatted_date}")
                print(f"Content: {content[:100]}...")

    def suggest_queries(self, prefix):
        return self.history_manager.suggest_queries(prefix)
