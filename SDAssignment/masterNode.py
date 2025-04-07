from flask import Flask, request, jsonify
import requests
from resultCache import ResultCache

app = Flask(__name__)
cache = ResultCache()

WORKER_URLS = [
    "http://localhost:3001/api/search",
    "http://localhost:3002/api/search"
]

def query_workers(query):
    all_results = []
    for url in WORKER_URLS:
        try:
            resp = requests.get(url, params={"q": query})
            if resp.status_code == 200:
                all_results.extend(resp.json())
        except Exception as e:
            print(f"Error querying {url}: {e}")
    return sorted(all_results)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    cached = cache.get(query)
    if cached:
        return jsonify(cached)

    results = query_workers(query)
    cache.set(query, results)
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=3000)
