import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
import os
import platform
import sys

class VideoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python VLC Video Player")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.video_path = None

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Video display area
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Control panel
        control_panel = tk.Frame(self)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM)

        open_button = tk.Button(control_panel, text="Open", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5, pady=5)

        play_button = tk.Button(control_panel, text="Play", command=self.play_video)
        play_button.pack(side=tk.LEFT, padx=5, pady=5)

        pause_button = tk.Button(control_panel, text="Pause", command=self.pause_video)
        pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        stop_button = tk.Button(control_panel, text="Stop", command=self.stop_video)
        stop_button.pack(side=tk.LEFT, padx=5, pady=5)

    def open_file(self):
        filetypes = [("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Open Video File", filetypes=filetypes)
        if filepath:
            self.video_path = filepath
            self.initialize_player()

    def initialize_player(self):
        if self.player.is_playing():
            self.player.stop()

        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)
        self.set_video_window()

    def set_video_window(self):
        # Ensure the video frame is rendered
        self.video_frame.update_idletasks()

        if platform.system() == 'Windows':
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif platform.system() == 'Darwin':  # macOS
            self.player.set_nsobject(self.video_frame.winfo_id())
        else:  # Linux and others
            self.player.set_xwindow(self.video_frame.winfo_id())

    def play_video(self):
        if not self.video_path:
            messagebox.showwarning("No Video", "Please open a video file first.")
            return
        self.player.play()

    def pause_video(self):
        if self.player.is_playing():
            self.player.pause()

    def stop_video(self):
        if self.player.is_playing():
            self.player.stop()

    def on_close(self):
        if self.player:
            self.player.stop()
        self.destroy()

if __name__ == "__main__":
    app = VideoPlayer()
    app.mainloop()
