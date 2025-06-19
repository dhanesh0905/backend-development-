import uuid
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flasgger import Swagger
import streamlit as st

# Initialize Flask app
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Friendly To-Do API',
    'description': 'A warm and human-centered task manager ✨',
    'version': '1.0',
    'termsOfService': 'https://example.com/tos',
    'contact': {'name': 'Task Support', 'email': 'help@friendlytasks.com'},
}
Swagger(app)

# In-memory database
todos = []

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

def random_encouragement():
    """Return random motivational message"""
    encouragements = [
        "Progress, not perfection!",
        "You're doing amazing!",
        "One task at a time - you've got this!",
        "Every small step counts!",
        "Be proud of what you've accomplished today!"
    ]
    return random.choice(encouragements)
