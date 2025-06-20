import uuid #generate unique ids for the task
import random #random encounter messages 
from datetime import datetime  #timestamps 
from flask import Flask, jsonify, request   #web framework
from flasgger import Swagger   #api documents 
import streamlit as st    #gui

# Initialize Flask app
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'To-Do API',  #the frienndly made it sound corny 
    'description': 'A warm and human-centered task manager ✨',
    'version': '1.0',
    'contact': {'name': 'Task Support', 'email': 'help@friendlytasks.com'},
}
Swagger(app)

# In-memory database
todos = []  #list to store tasks 

# Helper functions
def human_response(message, status='success', **kwargs):
    """Create human-friendly JSON responses"""
    return {'status': status, 'message': message, **kwargs}

def human_task(task):
    """Add human touches to task objects"""
    emoji = '✅' if task['completed'] else '⏳'
    priority_icons = {'high': '❗️', 'medium': '🔸', 'low': '🔹'}
    return {
        **task,
        'display': f"{emoji} {priority_icons.get(task['priority'], '📝')} {task['title']}",
        'status_text': "Completed! Great job!" if task['completed'] else "In progress - you've got this!"
    }

#make it more friendly and cheary and motivational
def random_encouragement():
    """Return random motivational message"""
    encouragements = [
        "You're doing amazing!",
        "One task at a time - you've got this!",
        "Every small step counts!",
        "Be proud of what you've accomplished today!"
    ]
    return random.choice(encouragements)

# retrive all tasks human task to make it more friendly random encounter for chearing
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Get all tasks
    ---
    responses:
      200:
        description: List of humanized tasks
        examples:
          tasks: [{id: '...', title: 'Buy milk', completed: false}]
    """
    return jsonify({
        'tasks': [human_task(t) for t in todos],
        'count': len(todos),
        'encouragement': random_encouragement()
    })


#make new tasks 
@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: Water the plants
            priority:
              type: string
              enum: [high, medium, low]
              default: medium
    responses:
      201:
        description: Task created
        examples:
          message: Task created! 🌱
    """
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
#mark complete tasks \ mark tasks as complete 
@app.route('/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """
    Mark task as completed
    ---
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Task marked complete
        examples:
          message: Great job completing this task! 🎉
      404:
        description: Task not found
    """
    task = next((t for t in todos if t['id'] == task_id), None)
    if not task:
        return jsonify(human_response("Task not found", "error")), 404
        
    task['completed'] = True
    task['completed_at'] = datetime.now().isoformat()
    return jsonify(human_response("congrats !! u completed a task ! 🎉", task=human_task(task)))


#delete the tasks 
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task
    ---
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Task deleted
        examples:
          message: Task removed! Making space for new accomplishments 🌈
      404:
        description: Task not found
    """
    global todos
    initial_count = len(todos)
    todos = [t for t in todos if t['id'] != task_id]
    
    if len(todos) == initial_count:
        return jsonify(human_response("Task not found", "error")), 404
        
    return jsonify(human_response("Task removed! Making space for new accomplishments 🌈"))

#streamlit 
def run_streamlit():
    st.set_page_config(page_title="Friendly To-Do List", page_icon="✅", layout="centered")
    
    st.title("✨ Friendly Task Manager")
    st.caption("Your warm and encouraging productivity companion")
    
#form for task creation 
    with st.form("new_task", clear_on_submit=True):
        title = st.text_input("What would you like to accomplish?", placeholder="Enter task...")
        priority = st.selectbox("Priority", ["medium", "high", "low"], index=0)
        submitted = st.form_submit_button("Add Task 🌱")
        
        if submitted and title:
            response = app.test_client().post('/tasks', json={
                'title': title, 
                'priority': priority
            })
            if response.status_code == 201:
                st.success("Task added successfully!")
            else:
                st.error("Failed to add task")
    # Task list
    st.subheader("Your Tasks")
    if not todos:
        st.info("No tasks yet! Add your first task above.", icon="ℹ️")
    
    for task in todos:
        task_id = task['id']
        cols = st.columns([0.1, 0.6, 0.2, 0.1])
        
        with cols[0]:
            # Checkbox for completion
            if st.checkbox("", key=f"complete_{task_id}", value=task['completed']):
                if not task['completed']:
                    response = app.test_client().put(f'/tasks/{task_id}/complete')
                    if response.status_code == 200:
                        st.experimental_rerun()
              
        with cols[1]:
            # Task display with priority indicator
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
            # Delete button
            if st.button("🗑️", key=f"delete_{task_id}"):
                response = app.test_client().delete(f'/tasks/{task_id}')
                if response.status_code == 200:
                    st.experimental_rerun()
    
    # Encouragement section
    st.divider()
    st.subheader("💌 Encouragement Corner")
    if st.button("I need motivation!"):
        st.success(random_encouragement())
        
 # API documentation link
    st.markdown("---")
    st.markdown("### API Documentation")
    st.markdown("Our backend API follows OpenAPI standards: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)")
# Run both apps
if __name__ == '__main__':
    import threading
    import webbrowser
    
    # Start Flask in background thread
    threading.Thread(target=app.run, daemon=True).start()
    
    # Open browser to Streamlit frontend
    webbrowser.open("http://localhost:8501")
    
    # Start Streamlit frontend
    import streamlit.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", __file__, "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())