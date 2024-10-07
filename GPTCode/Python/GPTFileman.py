import os
import shutil
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def list_directory(path):
    global current_path
    current_path = path
    dir_list.delete(0, tk.END)
    path_label.config(text=current_path)
    try:
        for item in os.listdir(path):
            dir_list.insert(tk.END, item)
    except PermissionError:
        messagebox.showerror("Permission Denied", "You do not have permission to access this folder.")

def open_file(path):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', path))
    elif os.name == 'nt':
        os.startfile(path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', path))

def on_double_click(event):
    selection = dir_list.curselection()
    if selection:
        index = selection[0]
        selected = dir_list.get(index)
        path = os.path.join(current_path, selected)
        if os.path.isdir(path):
            list_directory(path)
        elif os.path.isfile(path):
            open_file(path)

def delete_item():
    selection = dir_list.curselection()
    if selection:
        index = selection[0]
        selected = dir_list.get(index)
        path = os.path.join(current_path, selected)
        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete '{selected}'?")
        if confirm:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                list_directory(current_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))

def rename_item():
    selection = dir_list.curselection()
    if selection:
        index = selection[0]
        selected = dir_list.get(index)
        old_path = os.path.join(current_path, selected)
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=selected)
        if new_name:
            new_path = os.path.join(current_path, new_name)
            try:
                os.rename(old_path, new_path)
                list_directory(current_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))

def new_folder():
    folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
    if folder_name:
        path = os.path.join(current_path, folder_name)
        try:
            os.mkdir(path)
            list_directory(current_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

def copy_item():
    selection = dir_list.curselection()
    if selection:
        index = selection[0]
        selected = dir_list.get(index)
        source = os.path.join(current_path, selected)
        dest_dir = filedialog.askdirectory(title="Select destination directory")
        if dest_dir:
            dest = os.path.join(dest_dir, selected)
            try:
                if os.path.isfile(source):
                    shutil.copy2(source, dest)
                elif os.path.isdir(source):
                    shutil.copytree(source, dest)
                list_directory(current_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))

def move_item():
    selection = dir_list.curselection()
    if selection:
        index = selection[0]
        selected = dir_list.get(index)
        source = os.path.join(current_path, selected)
        dest_dir = filedialog.askdirectory(title="Select destination directory")
        if dest_dir:
            dest = os.path.join(dest_dir, selected)
            try:
                shutil.move(source, dest)
                list_directory(current_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Simple Python File Manager")

# Set dark theme colors
bg_color = "#2e2e2e"        # Dark background color
fg_color = "#ffffff"        # Light text color
button_bg = "#3e3e3e"       # Button background
button_fg = "#ffffff"       # Button text color
highlight_color = "#555555" # Highlight color for selections and active elements

root.configure(bg=bg_color)

current_path = os.getcwd()

path_label = tk.Label(root, text=current_path, bg=bg_color, fg=fg_color)
path_label.pack(fill=tk.X)

toolbar = tk.Frame(root, bg=bg_color)
toolbar.pack(fill=tk.X)

up_button = tk.Button(toolbar, text="Up", command=lambda: list_directory(os.path.dirname(current_path)),
                      bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
up_button.pack(side=tk.LEFT, padx=2, pady=2)

copy_button = tk.Button(toolbar, text="Copy", command=copy_item,
                        bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
copy_button.pack(side=tk.LEFT, padx=2, pady=2)

move_button = tk.Button(toolbar, text="Move", command=move_item,
                        bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
move_button.pack(side=tk.LEFT, padx=2, pady=2)

delete_button = tk.Button(toolbar, text="Delete", command=delete_item,
                          bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
delete_button.pack(side=tk.LEFT, padx=2, pady=2)

rename_button = tk.Button(toolbar, text="Rename", command=rename_item,
                          bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
rename_button.pack(side=tk.LEFT, padx=2, pady=2)

new_folder_button = tk.Button(toolbar, text="New Folder", command=new_folder,
                              bg=button_bg, fg=button_fg, activebackground=highlight_color, activeforeground=fg_color)
new_folder_button.pack(side=tk.LEFT, padx=2, pady=2)

frame = tk.Frame(root, bg=bg_color)
frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, bg=bg_color, troughcolor=bg_color, highlightcolor=bg_color)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

dir_list = tk.Listbox(frame, yscrollcommand=scrollbar.set, bg=bg_color, fg=fg_color,
                      selectbackground=highlight_color, selectforeground=fg_color)
dir_list.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=dir_list.yview)

dir_list.bind('<Double-Button-1>', on_double_click)

list_directory(current_path)

root.mainloop()
