import os
import time
from copy import deepcopy
from jsonStorage import JsonStorage

class SearchProxy:
    def __init__(self, search_engine):
        self.engine = search_engine
        self.cache_storage = JsonStorage("search_cache.json")

    def search(self, query):
        key = query.lower()
        cache = self.cache_storage.data
        need_refresh = False

        if key in cache:
            cached_results = deepcopy(cache[key])
            cached_filepaths = set(r.get('filepath') for r in cached_results if r.get('filepath'))
            fresh_results = self.engine.search(query)
            fresh_filepaths = set(r.get('filepath') for r in fresh_results if r.get('filepath'))

            if cached_filepaths != fresh_filepaths:
                need_refresh = True
            else:
                for r in cached_results:
                    filepath = r.get('filepath')
                    filename = r.get('filename')
                    db_timestamp = self.engine.db.get_file_timestamp(filepath)
                    db_filename = os.path.basename(filepath) if filepath else None
                    if isinstance(db_timestamp, (float, int)):
                        db_ts_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(db_timestamp))
                    else:
                        db_ts_str = str(db_timestamp)
                    if db_ts_str != r.get('timestamp', '') or db_filename != filename or not filepath:
                        need_refresh = True
                        break

            if need_refresh:
                results = fresh_results
                cache[key] = deepcopy(results)
                self.cache_storage.save()
                cache_status = "Cache miss – updated file(s), performed fresh search."
            else:
                results = cached_results
                cache_status = "Cache hit – results loaded from cache."
        else:
            results = self.engine.search(query)
            cache[key] = deepcopy(results)
            self.cache_storage.save()
            cache_status = "Cache miss – performed fresh search."

        return results, cache_status

