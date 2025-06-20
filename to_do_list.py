import uuid
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flasgger import Swagger
import streamlit as st
import threading
import webbrowser
import os
import sys

# Initialize Flask app
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'To-Do API',
    'description': 'A warm and human-centered task manager ✨',
    'version': '1.0',
    'contact': {'name': 'Task Support', 'email': 'help@friendlytasks.com'},
}
Swagger(app)

# In-memory database
todos = []

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

# Flask API endpoints
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({
        'tasks': [human_task(t) for t in todos],
        'count': len(todos),
        'encouragement': random_encouragement()
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify(human_response('Task title is required!', 'error')), 400
        
    new_task = {
        'id': str(uuid.uuid4()),
        'title': data['title'].strip(),
        'description': data.get('description', '').strip(),
        'created': datetime.now().isoformat(),
        'completed': False,
        'priority': data.get('priority', 'medium')
    }
    todos.append(new_task)
    return jsonify(human_response("Task created! 🌱", task=human_task(new_task))), 201

@app.route('/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    task = next((t for t in todos if t['id'] == task_id), None)
    if not task:
        return jsonify(human_response("Task not found", "error")), 404
        
    task['completed'] = True
    task['completed_at'] = datetime.now().isoformat()
    return jsonify(human_response("Congrats!! You completed a task! 🎉", task=human_task(task)))

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global todos
    initial_count = len(todos)
    todos = [t for t in todos if t['id'] != task_id]
    
    if len(todos) == initial_count:
        return jsonify(human_response("Task not found", "error")), 404
        
    return jsonify(human_response("Task removed! Making space for new accomplishments 🌈"))

# Streamlit UI
def run_streamlit():
    st.set_page_config(page_title="Friendly To-Do List", page_icon="✅", layout="centered")
    
    st.title("✨ Friendly Task Manager")
    st.caption("Your warm and encouraging productivity companion")
    
    with st.form("new_task", clear_on_submit=True):
        title = st.text_input("What would you like to accomplish?", placeholder="Enter task...")
        priority = st.selectbox("Priority", ["medium", "high", "low"], index=0)
        submitted = st.form_submit_button("Add Task 🌱")
        
        if submitted and title:
            with app.test_client() as client:
                response = client.post('/tasks', json={'title': title, 'priority': priority})
            if response.status_code == 201:
                st.success("Task added successfully!")
            else:
                st.error("Failed to add task")
    
    st.subheader("Your Tasks")
    if not todos:
        st.info("No tasks yet! Add your first task above.", icon="ℹ️")
    
    for task in todos:
        task_id = task['id']
        cols = st.columns([0.1, 0.6, 0.2, 0.1])
        
        with cols[0]:
            if st.checkbox("", key=f"complete_{task_id}", value=task['completed']):
                if not task['completed']:
                    with app.test_client() as client:
                        response = client.put(f'/tasks/{task_id}/complete')
                    if response.status_code == 200:
                        st.experimental_rerun()
              
        with cols[1]:
            priority_icon = {
                'high': '❗️ High', 
                'medium': '🔸 Medium', 
                'low': '🔹 Low'
            }.get(task['priority'], '📝')
            
            status = "~~" if task['completed'] else ""
            st.markdown(f"{status}{priority_icon} **{task['title']}**{status}")
            if task['description']:
                st.caption(task['description'])
        
        with cols[3]:
            if st.button("🗑️", key=f"delete_{task_id}"):
                with app.test_client() as client:
                    response = client.delete(f'/tasks/{task_id}')
                if response.status_code == 200:
                    st.experimental_rerun()
    
    st.divider()
    st.subheader("💌 Encouragement Corner")
    if st.button("I need motivation!"):
        st.success(random_encouragement())
        
    st.markdown("---")
    st.markdown("### API Documentation")
    st.markdown("Our backend API follows OpenAPI standards: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)")

# Execution control
if __name__ == '__main__':
    if os.environ.get("RUNNING_IN_STREAMLIT") != "true":
        # First execution: Launch Flask and Streamlit
        os.environ["RUNNING_IN_STREAMLIT"] = "true"
        
        # Start Flask in background thread
        threading.Thread(target=app.run, daemon=True).start()
        
        # Launch browser
        webbrowser.open("http://localhost:8501")
        
        # Run Streamlit normally
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", __file__, "--server.port=8501"]
        sys.exit(stcli.main())
    else:
        # Subsequent execution: Only run Streamlit UI
        run_streamlit()