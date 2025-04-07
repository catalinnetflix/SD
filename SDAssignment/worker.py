from flask import Flask, request, jsonify
import os
import sys
app = Flask(__name__)
ROOT_PATH = "C:/Users/Cata/Desktop/sdProject/test_files"

def search_files(query):
    results = []
    for dirpath, _, filenames in os.walk(ROOT_PATH):
        for file in filenames:
            if query.lower() in file.lower():
                results.append(os.path.join(dirpath, file))
    return results

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results = search_files(query)
    return jsonify(results)


if __name__ == '__main__':
    port = int(sys.argv[1])
    ROOT_PATH = sys.argv[2]
    app.run(port=port)
