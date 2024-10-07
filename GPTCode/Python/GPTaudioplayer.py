import tkinter as tk
from tkinter import filedialog
import subprocess
import tempfile
import os
import pygame

def convert_to_wav(input_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_wav_path = temp_wav.name

    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-i', input_file,
        temp_wav_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        return temp_wav_path
    except subprocess.CalledProcessError as e:
        print("Error converting file:", e)
        return None

class AudioPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Player")
        self.playing = False
        self.paused = False
        self.audio_file = None
        self.converted_file = None

        pygame.mixer.init()

        self.select_button = tk.Button(master, text="Select Audio File", command=self.select_file)
        self.select_button.pack()

        self.play_button = tk.Button(master, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_button.pack()

        self.pause_button = tk.Button(master, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.pause_button.pack()

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_audio, state=tk.DISABLED)
        self.stop_button.pack()

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select Audio File")
        if file_path:
            # Convert to WAV if necessary
            if not file_path.lower().endswith('.wav'):
                converted_file = convert_to_wav(file_path)
                if converted_file:
                    self.audio_file = converted_file
                    self.converted_file = converted_file  # Keep track for cleanup
                else:
                    return
            else:
                self.audio_file = file_path
                self.converted_file = None

            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.paused = False
            self.playing = False
            pygame.mixer.music.load(self.audio_file)

    def play_audio(self):
        if not self.playing:
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False

    def pause_audio(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        # Cleanup temporary file if any
        if self.converted_file and os.path.exists(self.converted_file):
            os.unlink(self.converted_file)
            self.converted_file = None

    def on_close(self):
        self.stop_audio()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = AudioPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_close)
    root.mainloop()
