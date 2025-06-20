import uuid #generate unique ids for the task
import random #random encounter messages 
from datetime import datetime  #timestamps 
from flask import Flask, jsonify, request   #web framework
from flasgger import Swagger   #api documents 
import streamlit as st    #gui

#i think these should be all i need for what i am planning for the code 

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
    