class ResultCache:
    def __init__(self):
        self.cache = {}

    def get(self, query: str):
        return self.cache.get(query)

    def set(self, query: str, results: list):
        self.cache[query] = results
