import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from databaseManager import DatabaseManager
from fileIndexer import FileIndexer
from searchEngine import SearchEngine
from historyManager import HistoryManager

class FileSearchAppGUI:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.db = DatabaseManager()
        self.indexer = FileIndexer(root_dir, self.db)
        self.history_manager = HistoryManager()
        self.search_engine = SearchEngine(self.db, self.history_manager)
        self.report_format = "summary"

        self.window = tk.Tk()
        self.window.title("File Search App")
        self.window.geometry("400x400")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="File Search App", font=("Helvetica", 18)).pack(pady=20)

        tk.Button(self.window, text="Index Files", command=self.index_files, width=30).pack(pady=10)
        tk.Button(self.window, text="Set Report Format", command=self.set_report_format, width=30).pack(pady=10)
        tk.Button(self.window, text="Search Files", command=self.search_files, width=30).pack(pady=10)
        tk.Button(self.window, text="View Search History", command=self.view_history, width=30).pack(pady=10)
        tk.Button(self.window, text="Quit", command=self.quit_app, width=30, fg="red").pack(pady=20)

    def index_files(self):
        if not os.path.exists(self.indexer.root):
            os.makedirs(self.indexer.root)
            messagebox.showinfo("Directory Created", f"Directory created at {self.indexer.root}. Please add files and re-run.")
            return

        self.indexer.index()
        messagebox.showinfo("Indexing Complete", f"Files under {self.indexer.root} have been indexed.")

    def set_report_format(self):
        choice = simpledialog.askstring("Report Format", "Choose report format (summary/detailed):")
        if choice and choice.lower() in ["summary", "detailed"]:
            self.report_format = choice.lower()
            messagebox.showinfo("Report Format Set", f"Report format set to {self.report_format}.")
        else:
            messagebox.showerror("Invalid Input", "Please enter 'summary' or 'detailed'.")

    def search_files(self):
        query = simpledialog.askstring("Search", "Enter your search query (e.g., path:docs content:project):")
        if query:
            self.search_engine.search(query, self.report_format)

    def view_history(self):
        history = self.history_manager.view_history()
        if history:
            history_text = "\n".join(history)
        else:
            history_text = "No search history available."
        messagebox.showinfo("Search History", history_text)

    def quit_app(self):
        self.db.close()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    root = "C:/Users/Cata/PycharmProjects/SDIteration2/generated_dataset2"
    app = FileSearchAppGUI(root)
    app.run()
