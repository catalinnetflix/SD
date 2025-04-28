class QueryParser:
    def parse(self, query):
        parts = query.split()
        path_parts = []
        content_parts = []
        query_terms = []

        for part in parts:
            if part.startswith("path:"):
                path = part[len("path:"):].replace("/", "\\")
                path_parts.append(path)
            elif part.startswith("content:"):
                content_parts.append(part[len("content:"):])
            else:
                query_terms.append(part)

        path_query = " AND ".join(path_parts) if path_parts else None
        content_query = " AND ".join(content_parts) if content_parts else None
        return content_query, path_query, query_terms