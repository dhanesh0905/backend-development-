import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
import random
import os
from datetime import datetime

# JSON database file
DB_FILE = "todo_db.json"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("you can do it !!")
        self.root.geometry("800x500")
        
        # Create database file if needed
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w') as f:
                json.dump([], f)
        
        self.create_widgets()
        self.refresh_tasks()
        
    def create_widgets(self):
        # Task creation form
        ttk.Label(self.root, text="What would you like to accomplish?").pack(pady=5)
        
        self.title_entry = ttk.Entry(self.root, width=40)
        self.title_entry.pack(pady=5)
        
        ttk.Label(self.root, text="Details (optional):").pack(pady=5)
        self.desc_entry = ttk.Entry(self.root, width=40)
        self.desc_entry.pack(pady=5)
        
        ttk.Label(self.root, text="Priority:").pack(pady=5)
        self.priority_var = tk.StringVar(value="medium")
        priority_combo = ttk.Combobox(self.root, textvariable=self.priority_var, 
                                     values=["high", "medium", "low"], state="readonly")
        priority_combo.pack(pady=5)
        
        add_btn = ttk.Button(self.root, text="Add Task", command=self.add_task)
        add_btn.pack(pady=10)
        
        # Task list
        self.task_frame = ttk.Frame(self.root)
        self.task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Encouragement section
        ttk.Separator(self.root, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)
        
        self.encouragement_label = ttk.Label(self.root, text="", font=("Arial", 10, "italic"))
        self.encouragement_label.pack(pady=5)
        
        ttk.Button(self.root, text="Give me encouragement!", 
                  command=self.show_encouragement).pack(pady=5)
        
        self.progress_label = ttk.Label(self.root, text="", font=("Arial", 9))
        self.progress_label.pack(pady=5)
        
    def load_tasks(self):
        """Load tasks from JSON file"""
        if not os.path.exists(DB_FILE):
            return []
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
            
    def save_tasks(self, tasks):
        """Save tasks to JSON file"""
        with open(DB_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
            
    def random_encouragement(self):
        encouragements = [
            "You're doing amazing!",
            "One task at a time - you've got this!",
            "Every small step counts!",
            "Be proud of what you've accomplished today!"
        ]
        return random.choice(encouragements)
        
    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Input Error", "Task title is required!")
            return
            
        tasks = self.load_tasks()
        new_task = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': self.desc_entry.get().strip(),
            'created': datetime.now().isoformat(),
            'completed': False,
            'priority': self.priority_var.get()
        }
        tasks.append(new_task)
        self.save_tasks(tasks)
        
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.refresh_tasks()
        messagebox.showinfo("Success", "Task added successfully!")
        
    def complete_task(self, task_id):
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                break
        self.save_tasks(tasks)
        self.refresh_tasks()
        
    def delete_task(self, task_id):
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t['id'] != task_id]
        self.save_tasks(tasks)
        self.refresh_tasks()
        
    def show_encouragement(self):
        self.encouragement_label.config(text=self.random_encouragement())
        
    def refresh_tasks(self):
        # Clear existing tasks
        for widget in self.task_frame.winfo_children():
            widget.destroy()
            
        tasks = self.load_tasks()
        completed_count = sum(1 for t in tasks if t['completed'])
        
        # Update progress
        self.progress_label.config(text=f"Progress: {completed_count}/{len(tasks)} completed")
        
        if not tasks:
            ttk.Label(self.task_frame, text="No tasks yet! Add your first task above.").pack()
            return
            
        for task in tasks:
            frame = ttk.Frame(self.task_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # Priority indicator
            priority_colors = {'high': 'red', 'medium': 'orange', 'low': 'green'}
            canvas = tk.Canvas(frame, width=20, height=20, highlightthickness=0)
            canvas.create_oval(5, 5, 15, 15, fill=priority_colors.get(task['priority'], 'gray'))
            canvas.pack(side=tk.LEFT, padx=(0, 5))
            
            # Task info
            title_font = ("Arial", 10, "overstrike" if task['completed'] else "normal")
            title_label = ttk.Label(frame, text=task['title'], font=title_font)
            title_label.pack(side=tk.LEFT, anchor="w", fill=tk.X, expand=True)
            
            if task['description']:
                desc_label = ttk.Label(frame, text=task['description'], font=("Arial", 8))
                desc_label.pack(side=tk.LEFT, anchor="w", fill=tk.X, expand=True)
            
            # Action buttons
            if not task['completed']:
                ttk.Button(frame, text="✓", width=2, 
                          command=lambda tid=task['id']: self.complete_task(tid)).pack(side=tk.RIGHT, padx=2)
            
            ttk.Button(frame, text="✕", width=2, 
                      command=lambda tid=task['id']: self.delete_task(tid)).pack(side=tk.RIGHT, padx=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()