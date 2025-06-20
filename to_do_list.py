import uuid
import random
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flasgger import Swagger
import streamlit as st
import threading
import webbrowser

# Initialize Flask app
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'To-Do API',
    'description': 'A warm and human-centered task manager ✨',
    'version': '1.0',
    'contact': {'name': 'Task Support', 'email': 'help@friendlytasks.com'},
}
Swagger(app)

# JSON database file
DB_FILE = "todo_db.json"

# Helper functions
def human_response(message, status='success', **kwargs):
    return {'status': status, 'message': message, **kwargs}

def human_task(task):
    emoji = '✅' if task['completed'] else '⏳'
    priority_icons = {'high': '❗️', 'medium': '🔸', 'low': '🔹'}
    return {
        **task,
        'display': f"{emoji} {priority_icons.get(task['priority'], '📝')} {task['title']}",
        'status_text': "Completed! Great job!" if task['completed'] else "In progress - you've got this!"
    }

def random_encouragement():
    encouragements = [
        "You're doing amazing!",
        "One task at a time - you've got this!",
        "Every small step counts!",
        "Be proud of what you've accomplished today!"
    ]
    return random.choice(encouragements)

# Database functions
def load_tasks():
    """Load tasks from JSON file"""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(DB_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Flask API endpoints
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify({
        'tasks': [human_task(t) for t in tasks],
        'count': len(tasks),
        'encouragement': random_encouragement()
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify(human_response('Task title is required!', 'error')), 400
        
    tasks = load_tasks()
    new_task = {
        'id': str(uuid.uuid4()),
        'title': data['title'].strip(),
        'description': data.get('description', '').strip(),
        'created': datetime.now().isoformat(),
        'completed': False,
        'priority': data.get('priority', 'medium')
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(human_response("Task created! 🌱", task=human_task(new_task))), 201

@app.route('/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify(human_response("Task not found", "error")), 404
        
    task['completed'] = True
    task['completed_at'] = datetime.now().isoformat()
    save_tasks(tasks)
    return jsonify(human_response("Congrats!! You completed a task! 🎉", task=human_task(task)))

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    initial_count = len(tasks)
    tasks = [t for t in tasks if t['id'] != task_id]
    
    if len(tasks) == initial_count:
        return jsonify(human_response("Task not found", "error")), 404
        
    save_tasks(tasks)
    return jsonify(human_response("Task removed! Making space for new accomplishments 🌈"))

# Streamlit UI
def run_streamlit():
    st.set_page_config(page_title="Friendly To-Do List", page_icon="✅", layout="centered")
    
    st.title("✨ Friendly Task Manager")
    st.caption("Your warm and encouraging productivity companion")
    
    # Task creation form
    with st.form("new_task", clear_on_submit=True):
        title = st.text_input("What would you like to accomplish?", placeholder="Enter task...")
        description = st.text_area("Details (optional)", placeholder="Add more details...")
        priority = st.selectbox("Priority", ["medium", "high", "low"], index=0)
        submitted = st.form_submit_button("Add Task 🌱")
        
        if submitted and title:
            with app.test_client() as client:
                response = client.post('/tasks', json={
                    'title': title,
                    'description': description,
                    'priority': priority
                })
            if response.status_code == 201:
                st.success("Task added successfully!")
                st.balloons()
            else:
                st.error("Failed to add task")
    
    # Load tasks from API
    with app.test_client() as client:
        response = client.get('/tasks')
        if response.status_code == 200:
            tasks = response.json['tasks']
        else:
            st.error("Failed to load tasks")
            tasks = []
    
    # Display tasks
    st.subheader("Your Tasks")
    if not tasks:
        st.info("No tasks yet! Add your first task above.", icon="ℹ️")
    
    for task in tasks:
        task_id = task['id']
        cols = st.columns([0.1, 0.7, 0.2])
        
        with cols[0]:
            # Checkbox for completion
            if task['completed']:
                st.checkbox("", key=f"done_{task_id}", value=True, disabled=True)
            else:
                if st.checkbox("", key=f"complete_{task_id}", value=False):
                    with app.test_client() as client:
                        response = client.put(f'/tasks/{task_id}/complete')
                    if response.status_code == 200:
                        st.experimental_rerun()
        
        with cols[1]:
            # Task display
            title_style = "line-through" if task['completed'] else "none"
            st.markdown(
                f"<span style='text-decoration:{title_style}; font-size:18px;'>"
                f"{task['display']}</span>", 
                unsafe_allow_html=True
            )
            
            if task.get('description'):
                st.caption(task['description'])
                
            if task['completed']:
                completed_time = datetime.fromisoformat(task.get('completed_at', datetime.now().isoformat())).strftime("%b %d, %H:%M")
                st.caption(f"Completed at {completed_time}")
        
        with cols[2]:
            # Delete button
            if st.button("🗑️", key=f"delete_{task_id}"):
                with app.test_client() as client:
                    response = client.delete(f'/tasks/{task_id}')
                if response.status_code == 200:
                    st.experimental_rerun()
    
    # Stats and encouragement
    completed_count = sum(1 for t in tasks if t['completed'])
    total_count = len(tasks)
    
    st.divider()
    st.subheader("💌 Encouragement Corner")
    if st.button("I need motivation!"):
        st.success(f"_{random_encouragement()}_")
    
    st.metric("Your Progress", f"{completed_count}/{total_count} completed", 
              help="Celebrate your accomplishments!")

# Execution control
if __name__ == '__main__':
    # Create database file if needed
    if not os.path.exists(DB_FILE):
        save_tasks([])
    
    # Start Flask in background thread
    threading.Thread(target=app.run, kwargs={'port': 5000}, daemon=True).start()
    
    # Open browser to Streamlit
    webbrowser.open("http://localhost:8501")
    
    # Run Streamlit
    run_streamlit()