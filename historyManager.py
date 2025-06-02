from jsonStorage import JsonStorage

class HistoryManager:
    def __init__(self, history_file='search_history.json'):
        self.storage = JsonStorage(history_file)

    def record_query(self, query):
        history = self.storage.data
        history[query] = history.get(query, 0) + 1
        self.storage.save()


    def get_history(self):
        return sorted(self.storage.data.items(), key=lambda x: x[1], reverse=False)

