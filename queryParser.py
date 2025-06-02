import re

class QueryParser:
    def parse(self, query):

        path_matches = re.findall(r'path:([^\s]+(?:\s*(?:\&|\|)\s*[^\s]+)*)', query)
        content_matches = re.findall(r'content:([^\s]+(?:\s*(?:\&|\|)\s*[^\s]+)*)', query)

        cleaned = re.sub(r'(path|content):([^\s]+(?:\s*(?:\&|\|)\s*[^\s]+)*)', '', query)

        def split_terms(expr):
            parts = re.split(r'(\&|\|)', expr)
            terms = []
            op = None
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                if p == '&':
                    op = "AND"
                elif p == '|':
                    op = "OR"
                else:
                    terms.append((p, op))
                    op = None
            return terms


        path_terms = []
        for m in path_matches:
            path_terms.extend(split_terms(m))
        path_query = path_terms


        content_terms = []
        for m in content_matches:
            content_terms.extend(split_terms(m))
        content_query = content_terms


        query_terms = [t for t in cleaned.split() if t]

        return content_query, path_query, query_terms
