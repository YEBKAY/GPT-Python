import tkinter as tk
from tkinter import filedialog, messagebox
import os

class SimpleTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Text Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")  # Set main window background

        # Initialize filename
        self.filename = None

        # Create Text Widget with dark theme
        self.text_area = tk.Text(
            self.root,
            undo=True,
            wrap='word',
            bg="#1e1e1e",               # Text area background
            fg="#d4d4d4",               # Text area foreground (text color)
            insertbackground="#ffffff", # Cursor color
            selectbackground="#555555"  # Selection color
        )
        self.text_area.pack(fill=tk.BOTH, expand=1)

        # Create Menu Bar with dark theme
        self.menu_bar = tk.Menu(
            self.root,
            bg="#2b2b2b",
            fg="#d4d4d4",
            activebackground="#3c3c3c",
            activeforeground="#ffffff"
        )
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(
            self.menu_bar,
            tearoff=0,
            bg="#2b2b2b",
            fg="#d4d4d4",
            activebackground="#3c3c3c",
            activeforeground="#ffffff"
        )
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        self.file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        self.file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        self.file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.exit_editor)

        # Edit Menu
        self.edit_menu = tk.Menu(
            self.menu_bar,
            tearoff=0,
            bg="#2b2b2b",
            fg="#d4d4d4",
            activebackground="#3c3c3c",
            activeforeground="#ffffff"
        )
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        self.edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)

        # Bind Shortcuts
        self.bind_shortcuts()

    def new_file(self, event=None):
        if self.confirm_discard_changes():
            self.text_area.delete(1.0, tk.END)
            self.filename = None
            self.root.title("Untitled - Simple Text Editor")

    def open_file(self, event=None):
        if self.confirm_discard_changes():
            file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                   filetypes=[("All Files", "*.*"),
                                                              ("Text Documents", "*.txt")])
            if file_path:
                try:
                    with open(file_path, "r", encoding='utf-8') as file:
                        content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.INSERT, content)
                    self.filename = file_path
                    self.root.title(f"{os.path.basename(file_path)} - Simple Text Editor")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self, event=None):
        if self.filename:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.filename, "w", encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Saved", "File saved successfully.")
                self.text_area.edit_modified(False)  # Reset the modified flag after saving
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("All Files", "*.*"),
                                                            ("Text Documents", "*.txt")])
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, "w", encoding='utf-8') as file:
                    file.write(content)
                self.filename = file_path
                self.root.title(f"{os.path.basename(file_path)} - Simple Text Editor")
                messagebox.showinfo("Saved", "File saved successfully.")
                self.text_area.edit_modified(False)  # Reset the modified flag after saving
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def exit_editor(self, event=None):
        if self.confirm_discard_changes():
            self.root.destroy()

    def undo(self, event=None):
        try:
            self.text_area.edit_undo()
        except:
            pass

    def redo(self, event=None):
        try:
            self.text_area.edit_redo()
        except:
            pass

    def select_all(self, event=None):
        self.text_area.tag_add('sel', '1.0', 'end')

    def bind_shortcuts(self):
        self.text_area.bind('<Control-n>', self.new_file)
        self.text_area.bind('<Control-N>', self.new_file)
        self.text_area.bind('<Control-o>', self.open_file)
        self.text_area.bind('<Control-O>', self.open_file)
        self.text_area.bind('<Control-s>', self.save_file)
        self.text_area.bind('<Control-S>', self.save_file)
        self.text_area.bind('<Control-Shift-s>', self.save_as_file)
        self.text_area.bind('<Control-Shift-S>', self.save_as_file)
        self.text_area.bind('<Control-z>', self.undo)
        self.text_area.bind('<Control-Z>', self.undo)
        self.text_area.bind('<Control-y>', self.redo)
        self.text_area.bind('<Control-Y>', self.redo)
        self.text_area.bind('<Control-a>', self.select_all)
        self.text_area.bind('<Control-A>', self.select_all)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_editor)

    def confirm_discard_changes(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel("Unsaved Changes",
                                                 "Do you want to save changes before proceeding?")
            if response:  # Yes, save changes
                self.save_file()
                return True
            elif response is False:  # No, discard changes
                return True
            else:  # Cancel
                return False
        return True

def main():
    root = tk.Tk()
    app = SimpleTextEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
