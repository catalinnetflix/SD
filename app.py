from flask import Flask, render_template, request, jsonify
import os
from databaseManager import DatabaseManager
from fileIndexer import FileIndexer
from searchEngine import SearchEngine
from historyManager import HistoryManager
from spellingCorrector import SpellingCorrector
from searchProxy import SearchProxy

app = Flask(__name__)

ROOT_DIR = os.getcwd()
DB = DatabaseManager()
INDEXER = FileIndexer(ROOT_DIR, DB)
HISTORY_MANAGER = HistoryManager()

CUSTOM_VOCAB = ["qr","calculator", "weather", "project", "file", "data", "index", "content", "report", "time", "json", "csv", "py", "java", "pdf"]
CORRECTOR = SpellingCorrector(custom_words=CUSTOM_VOCAB)
BASE_ENGINE = SearchEngine(DB, HISTORY_MANAGER)
SEARCH_ENGINE = SearchProxy(BASE_ENGINE)

@app.route("/index-files", methods=["POST"])
def index_files():
    INDEXER.index()
    return jsonify({"status": "success", "message": "Indexing complete!"})



def get_metadata_summary(results):
    import datetime
    file_types = {}
    years = {}
    languages = {}

    ext_to_lang = {
        'PY': 'Python',
        'PYC': 'Python',
        'F90': 'Fortran',
        'XML': 'XML',
        'TXT': 'Text',
        'MD': 'Markdown',
        'CSV': 'CSV',
        'JSON': 'JSON',
        'HTML': 'HTML',

    }
    for r in results:
        ext = os.path.splitext(r['filename'])[1].replace('.', '').upper()
        file_types[ext] = file_types.get(ext, 0) + 1

        ts = r.get('timestamp')
        year = ""
        if ts:
            try:
                if isinstance(ts, str) and len(ts) >= 4 and ts[:4].isdigit():
                    year = ts[:4]
                elif isinstance(ts, (int, float)):
                    year = str(datetime.datetime.fromtimestamp(ts).year)
            except Exception:
                year = ""
        if year:
            years[year] = years.get(year, 0) + 1
        lang = ext_to_lang.get(ext, None)
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    return file_types, years, languages

@app.route("/", methods=["GET", "POST"])
def index():
    search_results = []
    metadata = {}
    corrected = None
    original_query = ""
    cache_status = ""
    widget = None
    report_type = request.form.get("report_type", "summary")
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        original_query = query

        corrected_query = CORRECTOR.correct(query)
        if corrected_query != query:
            corrected = corrected_query
            query = corrected_query

        q_lower = query.lower()
        if "calculator" in q_lower:
            widget = "calculator"
        elif "weather" in q_lower:
            widget = "weather"
        elif "calendar" in q_lower:
            widget = "calendar"
        elif "clock" in q_lower:
            widget = "clock"


        search_results, cache_status = SEARCH_ENGINE.search(query)

        ft, yrs, langs = get_metadata_summary(search_results)
        metadata = {
            "file_types": ft,
            "years": yrs,
            "languages": langs
        }


    history_list = HISTORY_MANAGER.get_history()[-20:]

    return render_template("index.html",
                           results=search_results,
                           metadata=metadata,
                           corrected=corrected,
                           original_query=original_query,
                           widget=widget,
                           report_type=report_type,
                           history=history_list,
                           cache_status=cache_status
                           )


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(HISTORY_MANAGER.get_history()[:20])

if __name__ == "__main__":
    app.run(debug=True)
