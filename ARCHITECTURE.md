# ARCHITECTURE.md

## Search Engine: Iteration 1 - Software Design 2025

## 1. Context Diagram

### Purpose
The Context Diagram provides a high-level view of the Search Engine system, showing its boundaries and interactions with external entities. It establishes the scope of Iteration 1: indexing and searching files locally.

### Diagram
![Context Diagram](context_diagram.png)

### Description
The Search Engine is a single system interacting with three external entities:
- **User**: The individual who uses the search engine by entering queries to find files.
- **Local File System**: The source of text files on the user's device, which the system crawls and indexes.
- **Database (PostgreSQL)**: Stores the indexed data (filenames, content previews, metadata) and supports full-text search queries.

---

## 2. Container Diagram

### Purpose
The Container Diagram zooms into the Search Engine system, breaking it into major deployable units (containers) and showing how they collaborate to achieve the functionality of crawling, indexing, and searching text files.

### Diagram
![Container Diagram](container_diagram.png)

### Description
The system is composed of four containers, interacting with the external entities (User, Local File System, and Database):
- **File Crawler**: Recursively traverses the local file system to identify and collect textual files.
- **Indexer**: Processes files by extracting text content and metadata (filename, size, timestamp) and stores the data in the PostgreSQL database.
- **Database (PostgreSQL)**: Stores indexed data (filenames, content previews, metadata) and supports full-text search queries using the `to_tsvector` and `to_tsquery` functions for searching content.
- **Search Interface**: Accepts user queries, retrieves matching results from the database, and displays them with previews.

---

## 3. Component Diagram (Indexer)

### Purpose
The Component Diagram provides a detailed view of the Indexer container, showing its internal components and how they process files for storage in the database. The Indexer is chosen because it’s central to transforming raw files into searchable data.

### Diagram
![Component Diagram](component_diagram.png)

### Description
The Indexer container consists of three components:
- **Metadata Extractor**: Collects file metadata, such as filename, extension, size, and modification timestamp.
- **Content Extractor**: Reads textual files and extracts the first few lines of content as a preview (if the file is a text-based file).
- **Database Writer**: Inserts the extracted text and metadata into the PostgreSQL database for storage and querying.

---
