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
