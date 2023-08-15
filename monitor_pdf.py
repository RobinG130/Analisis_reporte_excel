import os
import time
import tkinter as tk
from tkinter import Label, Text, Scrollbar, RIGHT, LEFT, BOTH, Y, END
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

class PDFMoverHandler(FileSystemEventHandler):
    def __init__(self, source_path, destination_path, app):
        self.source_path = source_path
        self.destination_path = destination_path
        self.app = app

    def move_existing_files(self):
        for filename in os.listdir(self.source_path):
            if filename.endswith(".pdf"):
                source_file = os.path.join(self.source_path, filename)
                destination = os.path.join(self.destination_path, filename)

                try:
                    shutil.copy(source_file, destination)
                    os.remove(source_file)
                    self.app.add_message(f"Moved {filename} to {self.destination_path}")
                except Exception as e:
                    self.app.add_message(f"Error moving {filename}: {e}")

    def on_created(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        if filename.endswith(".pdf"):
            source_file = event.src_path
            destination = os.path.join(self.destination_path, filename)

            try:
                shutil.copy(source_file, destination)
                os.remove(source_file)
                self.app.add_message(f"Moved {filename} to {self.destination_path}")
            except Exception as e:
                self.app.add_message(f"Error moving {filename}: {e}")

class PDFMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Mover")

        self.status_label = Label(root, text="Monitoring...")
        self.status_label.pack(padx=10, pady=10)

        self.message_text = Text(root, wrap=tk.WORD, height=10, width=40)
        self.message_text.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = Scrollbar(self.message_text)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.message_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.message_text.yview)

        source_path = self.load_path_from_file("source.txt")
        destination_path = self.load_path_from_file("destino.txt")

        self.handler = PDFMoverHandler(source_path, destination_path, self)
        self.handler.move_existing_files()  # Move existing files at startup
        self.observer = Observer()
        self.observer.schedule(self.handler, source_path, recursive=True)
        self.observer.start()

    def load_path_from_file(self, filename):
        with open(filename, "r") as file:
            return file.read().strip()

    def add_message(self, message):
        self.message_text.insert(END, f"{message}\n")
        self.message_text.see(END)

root = tk.Tk()
app = PDFMoverApp(root)
root.mainloop()
