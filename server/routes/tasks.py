# server/routes/tasks.py

from flask import Blueprint, request, jsonify
import os
from datetime import datetime

from server.utils.task_manager import TaskManager
from server.utils.key_check import verify_key_validity

tasks_bp = Blueprint('tasks', __name__)
task_manager = TaskManager()

@tasks_bp.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Fetch all current tasks"""
    try:
        return jsonify(task_manager.get_all_tasks())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/tasks/active-count', methods=['GET'])
def get_active_task_count():
    """Return count of all currently active tasks"""
    try:
        return jsonify({'active_count': task_manager.active_task_count()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    """
    Create a new botting task.
    Expects JSON with:
    - username
    - password
    - avg_wpm
    - min_accuracy
    - races
    - key
    """
    try:
        data = request.get_json()

        required_fields = ['username', 'password', 'avg_wpm', 'min_accuracy', 'races', 'key']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

        key = data['key']
        is_valid, reason = verify_key_validity(key)
        if not is_valid:
            return jsonify({'success': False, 'message': reason}), 401

        # Check slot availability
        current_usage = task_manager.task_count_for_key(key)
        allowed_slots = task_manager.get_slots_for_key(key)
        if current_usage >= allowed_slots:
            return jsonify({
                'success': False,
                'message': f'Key is already using all {allowed_slots} slot(s).'
            }), 403

        username = data['username'].strip()
        password = data['password']
        avg_wpm = int(data['avg_wpm'])
        min_accuracy = int(data['min_accuracy'])
        races = int(data['races'])

        task_id = f"{username}_{int(datetime.utcnow().timestamp())}"

        task_data = {
            "username": username,
            "password": password,
            "avg_wpm": avg_wpm,
            "min_accuracy": min_accuracy,
            "races": races,
            "key": key,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        task_manager.add_task(task_id, task_data)

        return jsonify({'success': True, 'message': 'Task created successfully.', 'task_id': task_id})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500


@tasks_bp.route('/api/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get the current status of a specific task"""
    try:
        status = task_manager.get_task_status(task_id)
        if status:
            return jsonify({'task_id': task_id, 'status': status})
        return jsonify({'error': 'Task not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a specific task by ID"""
    try:
        result = task_manager.cancel_task(task_id)
        if result:
            return jsonify({'success': True, 'message': 'Task cancelled.'})
        else:
            return jsonify({'success': False, 'message': 'Task not found or already cancelled.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
