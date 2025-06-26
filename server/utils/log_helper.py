# server/utils/log_helper.py

import os
import threading
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(__file__), '../../bot/logs')

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Lock for thread-safe file writes
_write_lock = threading.Lock()

def get_log_file_path(username: str) -> str:
    """
    Returns the full path for a given user's log file.
    """
    safe_username = ''.join(c for c in username if c.isalnum() or c in ('_', '-')).rstrip()
    filename = f"{safe_username}.log"
    return os.path.join(LOGS_DIR, filename)

def log_message(username: str, message: str):
    """
    Logs a timestamped message to the user's log file.
    Thread-safe.
    """
    log_file = get_log_file_path(username)
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    log_entry = f"[{timestamp}] {message}\n"
    
    with _write_lock:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

def log_error(username: str, error_msg: str):
    """
    Convenience function to log errors specifically.
    """
    log_message(username, f"ERROR: {error_msg}")

def log_task_event(username: str, event_msg: str):
    """
    Convenience function to log task-related events.
    """
    log_message(username, f"TASK: {event_msg}")

