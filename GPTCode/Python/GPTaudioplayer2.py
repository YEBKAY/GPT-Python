import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import simpleaudio as sa
import threading
import os

class AudioPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Python Audio Player")

        # Initialize playback variables
        self.play_obj = None
        self.is_paused = False
        self.current_audio = None
        self.audio_thread = None

        # Create UI elements
        self.load_button = tk.Button(master, text="Load Audio", command=self.load_audio)
        self.load_button.pack(pady=10)

        self.play_button = tk.Button(master, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_button.pack(pady=5)

        self.pause_button = tk.Button(master, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.pause_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_audio, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(master, text="No audio loaded")
        self.status_label.pack(pady=10)

    def load_audio(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("M4A files", "*.m4a"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Load audio using pydub
                self.current_audio = AudioSegment.from_file(file_path, format="m4a")
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                self.play_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load audio: {e}")

    def play_audio(self):
        if self.current_audio:
            if self.is_paused:
                # Resume playback
                self.play_obj.resume()
                self.is_paused = False
                self.status_label.config(text="Playing")
                self.pause_button.config(text="Pause")
            else:
                # Start new playback in a separate thread
                self.audio_thread = threading.Thread(target=self._playback)
                self.audio_thread.start()
                self.status_label.config(text="Playing")
            self.play_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def _playback(self):
        try:
            # Export AudioSegment to raw audio data
            raw_data = self.current_audio.raw_data
            num_channels = self.current_audio.channels
            bytes_per_sample = self.current_audio.sample_width
            sample_rate = self.current_audio.frame_rate

            # Create simpleaudio playback object
            self.play_obj = sa.play_buffer(raw_data, num_channels, bytes_per_sample, sample_rate)
            self.play_obj.wait_done()
            # Reset UI after playback finishes
            self.master.after(0, self.reset_ui)
        except Exception as e:
            messagebox.showerror("Error", f"Playback failed: {e}")

    def pause_audio(self):
        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.pause()
            self.is_paused = True
            self.status_label.config(text="Paused")
            self.pause_button.config(text="Resume")
            self.play_button.config(state=tk.NORMAL)
        elif self.play_obj and self.is_paused:
            self.play_obj.resume()
            self.is_paused = False
            self.status_label.config(text="Playing")
            self.pause_button.config(text="Pause")
            self.play_button.config(state=tk.DISABLED)

    def stop_audio(self):
        if self.play_obj:
            self.play_obj.stop()
            self.reset_ui()

    def reset_ui(self):
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")

def main():
    root = tk.Tk()
    root.geometry("300x250")
    app = AudioPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
