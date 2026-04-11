import time
import subprocess
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script_to_run, file_to_watch):
        self.script_to_run = script_to_run
        self.file_to_watch = os.path.abspath(file_to_watch)
        self.process = None
        self.start_server()

    def start_server(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

        # Ensure we run the entry point script (_server.py)
        self.process = subprocess.Popen([sys.executable, self.script_to_run])

    def on_modified(self, event):
        # Convert event path to absolute to ensure an accurate match
        if os.path.abspath(event.src_path) == self.file_to_watch:
            print(f"--- Change detected in {event.src_path}, reloading... ---")
            self.start_server()

if __name__ == "__main__":
    # The file you want to monitor for changes
    target_file = os.path.join("e2eeftp", "server", "server.py")
    # The file you want to actually execute
    execution_script = "_server.py"

    # We watch the directory where the target file lives
    watch_dir = os.path.dirname(target_file)
    
    if not os.path.exists(target_file):
        print(f"Error: Could not find {target_file}")
        sys.exit(1)

    event_handler = ReloadHandler(execution_script, target_file)
    observer = Observer()
    # We only need to watch the specific directory containing the target file
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    print(f"Monitoring {target_file}...")
    print(f"Executing {execution_script} on changes.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()