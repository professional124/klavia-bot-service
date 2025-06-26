from flask import Flask, render_template, request, jsonify, abort, send_from_directory
import json
import os
from threading import Lock

app = Flask(__name__, static_folder='static', template_folder='templates')

# Thread-safe data access
data_lock = Lock()

# Paths to data files
KEYS_FILE = 'bot/keys.txt'
TASK_DATA_FILE = 'bot/task_data.json'

# Load keys and their slot limits into memory
def load_keys():
    keys = {}
    if not os.path.exists(KEYS_FILE):
        return keys
    with open(KEYS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Format: key:slots (e.g. abc123:3)
            if ':' in line:
                key, slots = line.split(':', 1)
                try:
                    keys[key.strip()] = int(slots.strip())
                except ValueError:
                    keys[key.strip()] = 1
            else:
                keys[line] = 1
    return keys

# Load task data (dictionary of username -> task info)
def load_tasks():
    if not os.path.exists(TASK_DATA_FILE):
        return {}
    with open(TASK_DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# Save task data safely
def save_tasks(tasks):
    with open(TASK_DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Validate API key, check slot availability
def validate_key(key, tasks):
    keys = load_keys()
    if key not in keys:
        return False, 'Invalid key'
    max_slots = keys[key]
    # Count how many active tasks use this key
    used_slots = sum(1 for task in tasks.values() if task.get('key') == key and not task.get('completed', False))
    if used_slots >= max_slots:
        return False, f'No available slots for this key (max {max_slots})'
    return True, None

# Routes serving pages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pricing.html')
def pricing():
    return render_template('pricing.html')

@app.route('/admin.html')
def admin():
    return render_template('admin.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/submit.html')
def submit():
    return render_template('submit.html')

@app.route('/tasks.html')
def tasks():
    return render_template('tasks.html')

# Static files served automatically by Flask via static_folder='static'

# API endpoint to start a new botting task
@app.route('/api/start-task', methods=['POST'])
def start_task():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    username = data.get('username')
    password = data.get('password')
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    race_count = data.get('race_count')
    key = data.get('key')

    # Basic validation
    if not all([username, password, wpm, accuracy, race_count, key]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate key and slots
    with data_lock:
        tasks = load_tasks()
        valid, err = validate_key(key, tasks)
        if not valid:
            return jsonify({'error': err}), 403

        # Check if user already has an active task
        if username in tasks and not tasks[username].get('completed', False):
            return jsonify({'error': 'Task for this user is already active'}), 409

        # Create task
        task = {
            'username': username,
            'password': password,
            'wpm': wpm,
            'accuracy': accuracy,
            'race_count': race_count,
            'key': key,
            'progress': 0,
            'completed': False,
            'logs': [],
        }
        tasks[username] = task
        save_tasks(tasks)

    return jsonify({'success': True, 'message': 'Task started', 'task': task}), 201

# API to get current active tasks data
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    with data_lock:
        tasks = load_tasks()
    # Optionally, filter or sanitize sensitive info here before sending
    sanitized = {
        user: {
            'username': t['username'],
            'wpm': t['wpm'],
            'accuracy': t['accuracy'],
            'race_count': t['race_count'],
            'progress': t.get('progress', 0),
            'completed': t.get('completed', False),
        }
        for user, t in tasks.items()
    }
    return jsonify(sanitized)

# API to get number of active botted accounts (for live stats)
@app.route('/api/live-accounts', methods=['GET'])
def live_accounts():
    with data_lock:
        tasks = load_tasks()
    active_count = sum(1 for t in tasks.values() if not t.get('completed', False))
    return jsonify({'activeTasks': active_count})

# API endpoint for admin to verify key usage or manage keys (simple example)
@app.route('/api/keys', methods=['GET'])
def list_keys():
    # In production, protect this route (authentication)
    keys = load_keys()
    return jsonify(keys)

# Optional: endpoint to get logs or task details, implement as needed

if __name__ == '__main__':
    # Run in debug=False for production, adjust host/port accordingly
    app.run(host='0.0.0.0', port=5000, debug=True)
