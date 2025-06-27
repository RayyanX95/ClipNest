import os
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class RestartHandler(FileSystemEventHandler):
    def __init__(self, run_args):
        self.run_args = run_args
        self.process = self.start_process()

    def start_process(self):
        return subprocess.Popen([sys.executable] + self.run_args)

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"Change detected in {event.src_path}, restarting...")
            self.process.terminate()
            self.process.wait()
            self.process = self.start_process()


if __name__ == "__main__":
    run_args = ["main.py"]  # Change to your main entry point if needed
    event_handler = RestartHandler(run_args)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.terminate()
    observer.join()
