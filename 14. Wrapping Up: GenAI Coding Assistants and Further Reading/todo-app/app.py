#!/usr/bin/env python3
"""
Simple TODO Application

This application provides a RESTful API for managing tasks with the following features:
- Create new tasks with title and description
- Mark tasks as complete/incomplete
- Delete tasks
- View all tasks
"""

from flask import Flask, request, jsonify, render_template
import uuid
import os

app = Flask(__name__)

# In-memory storage for tasks
tasks = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks"""
    return jsonify(list(tasks.values()))

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    # Validate input
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    task_id = str(uuid.uuid4())
    new_task = {
        'id': task_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False
    }
    
    tasks[task_id] = new_task
    return jsonify(new_task), 201

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task's status"""
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    task = tasks[task_id]
    
    # Update task properties if provided
    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'completed' in data:
        task['completed'] = data['completed']
    
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    del tasks[task_id]
    return jsonify({"message": "Task deleted"}), 200

if __name__ == '__main__':
    # Use environment variable for port or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Set host to 0.0.0.0 to make it accessible from outside the container
    app.run(host='0.0.0.0', port=port, debug=True)
