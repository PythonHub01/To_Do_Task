import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
from cryptography.fernet import Fernet
import json
import os
import re
from datetime import datetime

class TaskManager:
    KEY_FILE = "secret.key"
    DATA_FILE = "tasks.json"

    def __init__(self):
        self._generate_key()
        self.cipher = Fernet(self._load_key())
        self.tasks = self._load_tasks()

    def _generate_key(self):
        if not os.path.exists(self.KEY_FILE):
            key = Fernet.generate_key()
            with open(self.KEY_FILE, "wb") as key_file:
                key_file.write(key)

    def _load_key(self):
        with open(self.KEY_FILE, "rb") as key_file:
            return key_file.read()

    def _load_tasks(self):
        if not os.path.exists(self.DATA_FILE):
            return []
        with open(self.DATA_FILE, "rb") as file:
            encrypted_data = file.read()
            if not encrypted_data:
                return []
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data)

    def _save_tasks(self):
        encrypted_data = self.cipher.encrypt(json.dumps(self.tasks).encode())
        with open(self.DATA_FILE, "wb") as file:
            file.write(encrypted_data)

    def is_valid_name(self, name):
        return bool(re.fullmatch(r'[a-zA-Z\s]+', name))

    def is_valid_date(self, date_str):
        return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str))
    
    def is_valid_text(self, text):
        return bool(re.fullmatch(r'[a-zA-Z\s]+', text))

    def add_task(self, name, date, description, priority, status):
        if not self.is_valid_name(name):
            messagebox.showerror("Error", "❌ Invalid name! Only letters are allowed.")
            return False
        if not self.is_valid_date(date):
            messagebox.showerror("Error", "❌ Invalid date! Please use YYYY-MM-DD format.")
            return False
        if not self.is_valid_text(description) or not self.is_valid_text(priority) or not self.is_valid_text(status):
            messagebox.showerror("Error", "❌ Invalid description, priority, or status! Only letters are allowed.")
            return False
        task = {"name": name, "date": date, "description": description, "priority": priority, "status": status}
        self.tasks.append(task)
        self._save_tasks()
        messagebox.showinfo("Success", "✅ Task added successfully!")
        return True

    def edit_task(self, index, name, date, description, priority, status):
        if not self.is_valid_name(name) or not self.is_valid_date(date) or not self.is_valid_text(description) or not self.is_valid_text(priority) or not self.is_valid_text(status):
            messagebox.showerror("Error", "❌ Invalid input! Please enter valid values.")
            return False
        if 0 <= index < len(self.tasks):
            self.tasks[index] = {"name": name, "date": date, "description": description, "priority": priority, "status": status}
            self._save_tasks()
            messagebox.showinfo("Success", "✅ Task updated successfully!")
            return True
        else:
            messagebox.showerror("Error", "❌ Invalid task index!")
            return False

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self._save_tasks()
            messagebox.showinfo("Success", "✅ Task deleted successfully!")
        else:
            messagebox.showerror("Error", "❌ Invalid task index!")

class TaskManagerApp:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager

        self.root.title("Task Manager")
        self.root.geometry("500x600")
        self.root.configure(bg="#282C34")

        self.task_listbox = tk.Listbox(self.root, bg="#3C4048", fg="white", font=("Arial", 12))
        self.task_listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(self.root, bg="#282C34")
        self.input_frame.pack(pady=5)

        tk.Label(self.input_frame, text="Name:", fg="white", bg="#282C34").grid(row=0, column=0)
        self.name_entry = tk.Entry(self.input_frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.input_frame, text="Date (YYYY-MM-DD):", fg="white", bg="#282C34").grid(row=1, column=0)
        self.date_entry = tk.Entry(self.input_frame)
        self.date_entry.grid(row=1, column=1)

        tk.Label(self.input_frame, text="Description:", fg="white", bg="#282C34").grid(row=2, column=0)
        self.desc_entry = tk.Entry(self.input_frame)
        self.desc_entry.grid(row=2, column=1)

        tk.Label(self.input_frame, text="Priority:", fg="white", bg="#282C34").grid(row=3, column=0)
        self.priority_entry = tk.Entry(self.input_frame)
        self.priority_entry.grid(row=3, column=1)

        tk.Label(self.input_frame, text="Status:", fg="white", bg="#282C34").grid(row=4, column=0)
        self.status_entry = tk.Entry(self.input_frame)
        self.status_entry.grid(row=4, column=1)

        self.button_frame = tk.Frame(self.root, bg="#282C34")
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(self.button_frame, text="Add Task", command=self.add_task, bg="#61AFEF", fg="white", font=("Arial", 12))
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit Task", command=self.edit_task, bg="#E5C07B", fg="white", font=("Arial", 12))
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Task", command=self.delete_task, bg="#E06C75", fg="white", font=("Arial", 12))
        self.delete_button.grid(row=0, column=2, padx=5)

        self.view_button = tk.Button(self.button_frame, text="View Task", command=self.view_task, bg="#98C379", fg="white", font=("Arial", 12))
        self.view_button.grid(row=0, column=3, padx=5)

        self.refresh_task_list()

    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.manager.tasks:
            task_text = f"{task['name']} - {task['date']} ({task['priority']})"
            self.task_listbox.insert(tk.END, task_text)

    def add_task(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        description = self.desc_entry.get()
        priority = self.priority_entry.get()
        status = self.status_entry.get()
        
        if self.manager.add_task(name, date, description, priority, status):
            self.refresh_task_list()
            self.name_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            self.status_entry.delete(0, tk.END)

    def edit_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "❌ No task selected!")
            return
        index = selected[0]
        task = self.manager.tasks[index]
        
        new_name = simpledialog.askstring("Edit Task", "New name:", initialvalue=task['name'])
        new_date = simpledialog.askstring("Edit Task", "New date (YYYY-MM-DD):", initialvalue=task['date'])
        new_desc = simpledialog.askstring("Edit Task", "New description:", initialvalue=task['description'])
        new_priority = simpledialog.askstring("Edit Task", "New priority:", initialvalue=task['priority'])
        new_status = simpledialog.askstring("Edit Task", "New status:", initialvalue=task['status'])
        
        if all([new_name, new_date, new_desc, new_priority, new_status]):
            self.manager.edit_task(index, new_name, new_date, new_desc, new_priority, new_status)
            self.refresh_task_list()

    def view_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "❌ No task selected!")
            return
        task = self.manager.tasks[selected[0]]
        details = (
            f"Name: {task['name']}\n"
            f"Date: {task['date']}\n"
            f"Description: {task['description']}\n"
            f"Priority: {task['priority']}\n"
            f"Status: {task['status']}"
        )
        messagebox.showinfo("Task Details", details)

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "❌ No task selected!")
            return
        index = selected[0]
        self.manager.delete_task(index)
        self.refresh_task_list()

if __name__ == "__main__":
    manager = TaskManager()
    root = tk.Tk()
    app = TaskManagerApp(root, manager)
    root.mainloop()