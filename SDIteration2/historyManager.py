import json
import os
import platform
from tkinter import messagebox


class HistoryManager:
    def __init__(self, history_file='search_history.json'):
        self.history_file = history_file
        self.history = {}
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {}

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def record_query(self, query):
        if query in self.history:
            self.history[query] += 1
        else:
            self.history[query] = 1
        self.save_history()

    def suggest_queries(self, prefix):
        return [q for q in self.history if q.startswith(prefix)]

    def query_popularity(self, query):
        return self.history.get(query, 0)

    def suggest_most_popular_query(self, prefix):
        suggestions = [(q, self.history.get(q, 0)) for q in self.history if q.startswith(prefix)]
        suggestions.sort(key=lambda x: x[1], reverse=True)

        if suggestions:
            return suggestions[0][0]
        return None

    def view_history(self):
        historyCache = 'search_cache.json'
        if os.path.exists(historyCache):
            try:
                os.startfile(historyCache)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open history file.\n{str(e)}")
        else:
            messagebox.showinfo("No History", "No search history available.")
