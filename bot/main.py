import asyncio
import json
import os
from flask import Flask, request, jsonify, render_template_string
from task_runner import TaskRunner

app = Flask(__name__)

task_runner = TaskRunner()

# Simple home page
HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>Klavia Bot</title></head>
<body>
<h1>Klavia Bot Running</h1>
<p>Use POST /start-task with JSON to queue a race task.</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/start-task', methods=['POST'])
def start_task():
    data = request.json
    required_fields = ['username', 'password', 'wpm', 'accuracy', 'races', 'key']

    # Validate input presence
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate key
    key = data['key']
    if key not in task_runner.key_slots:
        return jsonify({"error": "Invalid or unauthorized key"}), 403

    # Check slot availability
    if not task_runner.can_start_task(key):
        return jsonify({"error": "No available slots for this key. Try later."}), 429

    # Validate WPM, accuracy, races numeric ranges (example limits)
    try:
        wpm = int(data['wpm'])
        accuracy = int(data['accuracy'])
        races = int(data['races'])
    except ValueError:
        return jsonify({"error": "WPM, accuracy, and races must be integers"}), 400

    if not (10 <= wpm <= 180):
        return jsonify({"error": "WPM must be between 10 and 180"}), 400
    if not (85 <= accuracy <= 100):
        return jsonify({"error": "Accuracy must be between 85 and 100"}), 400
    if races < 1:
        return jsonify({"error": "Races must be at least 1"}), 400

    # Prepare task object
    task = {
        "username": data['username'],
        "password": data['password'],
        "wpm": wpm,
        "accuracy": accuracy,
        "races_total": races,
        "key_used": key,
        "status": "pending",
        "races_completed": 0,
        "started_at": None,
        "ended_at": None,
        "last_error": None
    }

    # Add task
    task_runner.add_task(task)

    return jsonify({"message": "Task queued successfully", "task_id": task["task_id"]})

# Run Flask and asyncio worker loop together
def run_app_and_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run Flask app in a separate thread so asyncio loop can run simultaneously
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False), daemon=True).start()

    # Run async worker loop forever
    loop.run_until_complete(task_runner.worker_loop())

if __name__ == '__main__':
    run_app_and_worker()
