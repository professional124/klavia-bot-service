
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

TASK_DATA_PATH = os.path.join(os.path.dirname(__file__), 'task_data.json')
KEYS_PATH = os.path.join(os.path.dirname(__file__), 'keys.txt')

class TaskRunner:
    def __init__(self):
        self.tasks = []
        self.active_tasks = {}
        self.key_slots = {}  # key: max slots
        self.load_keys()
        self.load_tasks()

    def load_keys(self):
        """Load keys and their slot limits from keys.txt"""
        self.key_slots.clear()
        if not os.path.exists(KEYS_PATH):
            print("Warning: keys.txt not found!")
            return
        with open(KEYS_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(':')
                if len(parts) == 2:
                    key, slots = parts
                    try:
                        self.key_slots[key] = int(slots)
                    except ValueError:
                        print(f"Invalid slot number for key {key}")
                else:
                    # Default to 1 slot if no colon found
                    self.key_slots[parts[0]] = 1

    def load_tasks(self):
        """Load tasks from JSON"""
        if not os.path.exists(TASK_DATA_PATH):
            self.tasks = []
            self.save_tasks()
            return
        with open(TASK_DATA_PATH, 'r') as f:
            try:
                data = json.load(f)
                self.tasks = data.get('tasks', [])
            except json.JSONDecodeError:
                print("Warning: task_data.json corrupted, resetting")
                self.tasks = []
                self.save_tasks()

    def save_tasks(self):
        """Save current tasks to JSON"""
        with open(TASK_DATA_PATH, 'w') as f:
            json.dump({"tasks": self.tasks}, f, indent=2)

    def can_start_task(self, key: str) -> bool:
        """Check if key has available slots"""
        max_slots = self.key_slots.get(key, 0)
        running_slots = sum(1 for t in self.active_tasks.values() if t['key_used'] == key)
        return running_slots < max_slots

    async def run_task(self, task: Dict):
        """Run a single bot task asynchronously"""
        task_id = task.get("task_id")
        username = task.get("username")
        key = task.get("key_used")

        # Mark task as running
        task["status"] = "in_progress"
        task["started_at"] = datetime.utcnow().isoformat() + "Z"
        self.active_tasks[task_id] = task
        self.save_tasks()
        print(f"Starting task {task_id} for {username}")

        try:
            # --- Your bot race logic goes here ---
            # Example: simulate race running
            races_total = task.get("races_total", 5)
            for i in range(task.get("races_completed", 0), races_total):
                # Simulate race typing
                print(f"Task {task_id}: Race {i+1}/{races_total}")
                await asyncio.sleep(2)  # simulate time to complete race

                # Update completed races
                task["races_completed"] = i + 1
                self.save_tasks()

            # Mark completed
            task["status"] = "completed"
            task["ended_at"] = datetime.utcnow().isoformat() + "Z"
            print(f"Completed task {task_id} for {username}")

        except Exception as e:
            task["status"] = "error"
            task["last_error"] = str(e)
            print(f"Error in task {task_id}: {e}")

        # Remove from active
        self.active_tasks.pop(task_id, None)
        self.save_tasks()

    async def worker_loop(self):
        """Main loop to run pending tasks when slots available"""
        while True:
            # Refresh keys and tasks regularly
            self.load_keys()
            self.load_tasks()

            # Find pending tasks
            pending_tasks = [t for t in self.tasks if t["status"] == "pending"]

            # For each pending task, check if can start based on key slots
            for task in pending_tasks:
                key = task.get("key_used")
                if self.can_start_task(key):
                    # Start task async, no await to let other tasks run
                    asyncio.create_task(self.run_task(task))

            # Sleep before next loop
            await asyncio.sleep(5)

    def add_task(self, task: Dict):
        """Add a new task to queue"""
        task["status"] = "pending"
        task["races_completed"] = 0
        task["started_at"] = None
        task["ended_at"] = None
        task["last_error"] = None
        task["task_id"] = f"task_{len(self.tasks) + 1:04d}"
        self.tasks.append(task)
        self.save_tasks()
        print(f"Added task {task['task_id']} for {task['username']}")

