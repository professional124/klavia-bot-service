# server/routes/auth.py

from flask import Blueprint, request, jsonify
import os

auth_bp = Blueprint('auth', __name__)
KEYS_FILE = os.path.join(os.path.dirname(__file__), '../../keys.txt')

def load_keys():
    keys = {}
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    key, slots = parts
                    keys[key.strip()] = int(slots.strip())
    return keys

def count_tasks_by_key(task_data, key):
    count = 0
    for task in task_data.values():
        if task.get('key') == key:
            count += 1
    return count

@auth_bp.route('/api/verify-key', methods=['POST'])
def verify_key():
    try:
        data = request.json
        key = data.get('key', '').strip()

        if not key:
            return jsonify({'success': False, 'message': 'No key provided.'}), 400

        valid_keys = load_keys()
        if key not in valid_keys:
            return jsonify({'success': False, 'message': 'Invalid key.'}), 401

        # Dynamically import the task manager
        from server.utils.task_manager import TaskManager
        manager = TaskManager()
        tasks = manager.get_all_tasks()
        current_count = count_tasks_by_key(tasks, key)
        allowed_slots = valid_keys[key]

        if current_count >= allowed_slots:
            return jsonify({
                'success': False,
                'message': f'Key is valid but currently in use on {current_count}/{allowed_slots} slots.'
            }), 403

        return jsonify({
            'success': True,
            'message': f'Key accepted. {allowed_slots - current_count} slots available.',
            'slots_available': allowed_slots - current_count
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500

