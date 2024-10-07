#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk here
import subprocess
import threading
import os
import sys
import queue

# Define allowed media file extensions
ALLOWED_EXTENSIONS = {
    '.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma',
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.flv'
}

def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        messagebox.showerror("ffmpeg Not Found", "ffmpeg is not installed or not in PATH.")
        sys.exit(1)

def convert_to_opus(input_file, output_file, bitrate, sample_rate):
    """Convert the input media file to an OPUS file with specified settings."""
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ar', sample_rate,    # Set audio sample rate
        '-c:a', 'libopus',
        '-b:a', bitrate,       # Set audio bitrate
        '-vbr', 'off',         # Attempt to force constant bitrate (may not be strictly enforced)
        '-vn',                 # Disable video recording
        output_file
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting '{input_file}': {e}")
        return False

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

def start_conversion():
    directory = directory_entry.get()
    bitrate = bitrate_entry.get()
    sample_rate = sample_rate_entry.get()
    recursive = recursive_var.get()

    if not os.path.isdir(directory):
        messagebox.showerror("Invalid Directory", "Please select a valid directory.")
        return

    if not bitrate.endswith('k'):
        messagebox.showerror("Invalid Bitrate", "Bitrate must end with 'k' (e.g., '8k').")
        return

    if not sample_rate.isdigit():
        messagebox.showerror("Invalid Sample Rate", "Sample rate must be a numeric value (e.g., '44100').")
        return

    # Disable the start button to prevent multiple clicks
    start_button.config(state=tk.DISABLED)

    # Clear progress bar and label
    progress_bar['value'] = 0
    progress_label.config(text="")

    # Create a queue to communicate with the thread
    q = queue.Queue()

    # Run the conversion in a separate thread to keep the GUI responsive
    threading.Thread(target=convert_directory, args=(directory, bitrate, sample_rate, recursive, q), daemon=True).start()

    # Start monitoring the queue
    root.after(100, lambda: check_queue(q))

def check_queue(q):
    try:
        message = q.get_nowait()
        if message['type'] == 'update':
            progress_label.config(text=message['text'])
            progress_bar['value'] = message['progress']
        elif message['type'] == 'done':
            progress_label.config(text=message['text'])
            start_button.config(state=tk.NORMAL)
            return
    except queue.Empty:
        pass
    # Continue checking the queue
    root.after(100, lambda: check_queue(q))

def convert_directory(directory, bitrate, sample_rate, recursive, q):
    check_ffmpeg()

    files_to_convert = []

    if recursive:
        for root_dir, dirs, files in os.walk(directory):
            for filename in files:
                base, ext = os.path.splitext(filename)
                if ext.lower() in ALLOWED_EXTENSIONS:
                    input_file = os.path.join(root_dir, filename)
                    output_file = os.path.join(root_dir, base + '.opus')
                    files_to_convert.append((input_file, output_file))
    else:
        for filename in os.listdir(directory):
            base, ext = os.path.splitext(filename)
            if ext.lower() in ALLOWED_EXTENSIONS:
                input_file = os.path.join(directory, filename)
                output_file = os.path.join(directory, base + '.opus')
                files_to_convert.append((input_file, output_file))

    total_files = len(files_to_convert)
    success_count = 0

    for idx, (input_file, output_file) in enumerate(files_to_convert, 1):
        result = convert_to_opus(input_file, output_file, bitrate, sample_rate)
        progress_percentage = (idx / total_files) * 100
        if result:
            success_count += 1
        # Put update message in the queue
        q.put({'type': 'update', 'text': f"Converting {idx} of {total_files} files...", 'progress': progress_percentage})

    # Put completion message in the queue
    q.put({'type': 'done', 'text': f"Conversion completed: {success_count}/{total_files} files converted."})

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        sys.exit(0)

# Create the main window
root = tk.Tk()
root.title("Media to OPUS Converter")

# Directory selection
directory_label = tk.Label(root, text="Select Directory:")
directory_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
directory_entry = tk.Entry(root, width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse...", command=select_directory)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Bitrate input
bitrate_label = tk.Label(root, text="Audio Bitrate (e.g., 8k):")
bitrate_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
bitrate_entry = tk.Entry(root)
bitrate_entry.insert(0, '8k')
bitrate_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

# Sample rate input
sample_rate_label = tk.Label(root, text="Sample Rate (e.g., 44100):")
sample_rate_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
sample_rate_entry = tk.Entry(root)
sample_rate_entry.insert(0, '44100')
sample_rate_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

# Recursive option
recursive_var = tk.BooleanVar()
recursive_check = tk.Checkbutton(root, text="Process subdirectories recursively", variable=recursive_var)
recursive_check.grid(row=3, column=1, padx=5, pady=5, sticky='w')

# Start button
start_button = tk.Button(root, text="Start Conversion", command=start_conversion)
start_button.grid(row=4, column=1, padx=5, pady=10)

# Progress display
progress_label = tk.Label(root, text="")
progress_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Set window close protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
