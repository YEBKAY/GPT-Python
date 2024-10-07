import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import os

# Constants for MCI
MCI_OPEN = 0x0803
MCI_PLAY = 0x0806
MCI_CLOSE = 0x0804
MCI_SEEK = 0x0805
MCI_STOP = 0x0807

# MCI command structure
class MCI_OPEN_PARMS(ctypes.Structure):
    _fields_ = [
        ("dwCallback", ctypes.c_ulong),
        ("lpstrDeviceType", ctypes.c_char_p),
        ("lpstrElementName", ctypes.c_char_p),
        ("dwAlias", ctypes.c_ulong),
    ]

class MCI_GENERIC_PARMS(ctypes.Structure):
    _fields_ = [
        ("dwCallback", ctypes.c_ulong),
    ]

class MCI_PLAY_PARMS(ctypes.Structure):
    _fields_ = [
        ("dwCallback", ctypes.c_ulong),
        ("dwFrom", ctypes.c_ulong),
        ("dwTo", ctypes.c_ulong),
    ]

# Load winmm library
winmm = ctypes.WinDLL('winmm')

def mci_send_string(command, buffer, buffer_size, hwnd):
    return winmm.mciSendStringA(
        command.encode('utf-8'),
        ctypes.create_string_buffer(buffer.encode('utf-8'), buffer_size),
        buffer_size,
        hwnd
    )

class VideoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Video Player")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.video_id = None
        self.video_path = None

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Video display area (a simple frame)
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Control panel
        control_panel = tk.Frame(self)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM)

        open_button = tk.Button(control_panel, text="Open", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5, pady=5)

        play_button = tk.Button(control_panel, text="Play", command=self.play_video)
        play_button.pack(side=tk.LEFT, padx=5, pady=5)

        stop_button = tk.Button(control_panel, text="Stop", command=self.stop_video)
        stop_button.pack(side=tk.LEFT, padx=5, pady=5)

    def open_file(self):
        filetypes = [("MP4 files", "*.mp4"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Open Video File", filetypes=filetypes)
        if filepath:
            self.video_path = filepath
            self.initialize_mci()

    def initialize_mci(self):
        if self.video_id:
            self.close_video()

        # Get the window handle for the video frame
        hwnd = self.video_frame.winfo_id()

        # Open the video file
        command = f'open "{self.video_path}" type mpegvideo alias myvideo parent {hwnd}'
        ret = mci_send_string(command, "", 0, 0)
        if ret:
            messagebox.showerror("Error", f"Failed to open video. Error code: {ret}")
            self.video_id = None
        else:
            self.video_id = 'myvideo'

    def play_video(self):
        if not self.video_id:
            messagebox.showwarning("No Video", "Please open a video file first.")
            return

        command = f'play {self.video_id} notify'
        ret = mci_send_string(command, "", 0, self.winfo_id())
        if ret:
            messagebox.showerror("Error", f"Failed to play video. Error code: {ret}")

    def stop_video(self):
        if not self.video_id:
            return
        command = f'stop {self.video_id}'
        ret = mci_send_string(command, "", 0, 0)
        if ret:
            messagebox.showerror("Error", f"Failed to stop video. Error code: {ret}")

    def close_video(self):
        if not self.video_id:
            return
        command = f'close {self.video_id}'
        ret = mci_send_string(command, "", 0, 0)
        if ret:
            messagebox.showerror("Error", f"Failed to close video. Error code: {ret}")
        self.video_id = None

    def on_close(self):
        self.close_video()
        self.destroy()

if __name__ == "__main__":
    app = VideoPlayer()
    app.mainloop()
