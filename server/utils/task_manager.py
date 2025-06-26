# server/utils/task_manager.py

import json
import os
import threading
from datetime import datetime

TASK_DATA_FILE = os.path.join(os.path.dirname(__file__), '../../task_data.json')

_lock = threading.Lock()

class TaskManager:
    def __init__(self, task_file=TASK_DATA_FILE):
        self.task_file = task_file
        self.tasks = {}
        self.load_tasks()

    def load_tasks(self):
        """
        Loads tasks from the JSON file.
        """
        with _lock:
            try:
                if os.path.exists(self.task_file):
                    with open(self.task_file, 'r', encoding='utf-8') as f:
                        self.tasks = json.load(f)
                else:
                    self.tasks = {}
            except Exception as e:
                print(f"[Error] Loading tasks failed: {e}")
                self.tasks = {}

    def save_tasks(self):
        """
        Saves current tasks dict to JSON file.
        """
        with _lock:
            try:
                with open(self.task_file, 'w', encoding='utf-8') as f:
                    json.dump(self.tasks, f, indent=4)
            except Exception as e:
                print(f"[Error] Saving tasks failed: {e}")

    def add_task(self, username, task_data):
        """
        Adds a new task for a user.
        task_data is a dict containing keys like:
          - username
          - avg_wpm
          - min_accuracy
          - races_to_run
          - status (e.g. pending, running, completed)
          - started_at (ISO datetime string)
          - ended_at (ISO datetime string)
          - progress (0 to 100)
        """
        with _lock:
            self.tasks[username] = task_data
            self.save_tasks()

    def update_task(self, username, updates):
        """
        Updates fields in an existing task.
        'updates' is a dict of keys to update.
        """
        with _lock:
            if username in self.tasks:
                self.tasks[username].update(updates)
                self.save_tasks()

    def remove_task(self, username):
        """
        Removes a task by username.
        """
        with _lock:
            if username in self.tasks:
                del self.tasks[username]
                self.save_tasks()

    def get_task(self, username):
        """
        Returns task data for a given username or None.
        """
        with _lock:
            return self.tasks.get(username)

    def get_all_tasks(self):
        """
        Returns all tasks dict.
        """
        with _lock:
            return dict(self.tasks)

    def purge_completed(self):
        """
        Removes tasks that are marked 'completed' or no longer active.
        """
        with _lock:
            to_delete = [user for user, data in self.tasks.items()
                         if data.get('status') == 'completed']
            for user in to_delete:
                del self.tasks[user]
            if to_delete:
                self.save_tasks()

    def count_active(self):
        """
        Returns number of tasks with status not completed.
        """
        with _lock:
            return sum(1 for data in self.tasks.values() if data.get('status') != 'completed')

# Usage example:
# if __name__ == '__main__':
#     manager = TaskManager()
#     manager.add_task('user1', {
#         'username': 'user1',
#         'avg_wpm': 60,
#         'min_accuracy': 95,
#         'races_to_run': 10,
#         'status': 'pending',
#         'started_at': None,
#         'ended_at': None,
#         'progress': 0
#     })
#     print(manager.get_all_tasks())
