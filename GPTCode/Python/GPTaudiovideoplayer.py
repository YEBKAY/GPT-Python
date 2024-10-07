import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import tempfile
import os
import sys
import time
import struct
import winsound

class VideoPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Video Player")

        # Initialize UI elements
        self.canvas = tk.Canvas(master, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(master)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.play_button = tk.Button(control_frame, text="Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_video, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_button = tk.Button(control_frame, text="Open", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Video and audio handling
        self.video_process = None
        self.audio_process = None
        self.audio_thread = None
        self.display_thread = None
        self.stop_event = threading.Event()
        self.frame_rate = 30  # Default frame rate
        self.width = 640       # Default width
        self.height = 480      # Default height

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if file_path:
            self.video_path = file_path
            self.play_button.config(state=tk.NORMAL)

    def play_video(self):
        if not hasattr(self, 'video_path'):
            messagebox.showerror("Error", "No video file selected.")
            return

        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_event.clear()

        # Extract audio to a temporary WAV file
        self.temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio_cmd = [
            "ffmpeg",
            "-i", self.video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            self.temp_audio.name,
            "-y"  # Overwrite without prompt
        ]

        try:
            subprocess.run(audio_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to extract audio.")
            self.play_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return

        # Start audio playback in a separate thread
        self.audio_thread = threading.Thread(target=self.play_audio, args=(self.temp_audio.name,))
        self.audio_thread.start()

        # Extract video information (frame rate, resolution)
        self.get_video_info()

        # Start video playback
        self.display_thread = threading.Thread(target=self.display_video)
        self.display_thread.start()

    def get_video_info(self):
        cmd = [
            "ffmpeg",
            "-i", self.video_path
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            info = result.stderr

            # Extract frame rate
            import re
            fps_search = re.search(r'(\d+(?:\.\d+)?) fps', info)
            if fps_search:
                self.frame_rate = float(fps_search.group(1))
            else:
                self.frame_rate = 30  # Default

            # Extract resolution
            res_search = re.search(r'(\d+)x(\d+)', info)
            if res_search:
                self.width = int(res_search.group(1))
                self.height = int(res_search.group(2))
            else:
                self.width = 640
                self.height = 480

            # Update canvas size
            self.canvas.config(width=self.width, height=self.height)

        except Exception as e:
            print(f"Error getting video info: {e}")
            self.frame_rate = 30
            self.width = 640
            self.height = 480

    def play_audio(self, audio_file):
        try:
            winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def display_video(self):
        # FFmpeg command to extract raw RGB frames
        video_cmd = [
            "ffmpeg",
            "-i", self.video_path,
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-"
        ]

        try:
            self.video_process = subprocess.Popen(video_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start video process: {e}")
            self.stop_video()
            return

        frame_size = self.width * self.height * 3  # RGB24
        delay = 1 / self.frame_rate

        try:
            while not self.stop_event.is_set():
                raw_frame = self.video_process.stdout.read(frame_size)
                if len(raw_frame) < frame_size:
                    break  # End of video

                # Convert raw data to PhotoImage
                image = tk.PhotoImage(width=self.width, height=self.height)
                # PhotoImage expects data in PPM format, so we need to convert
                ppm_header = f"P6 {self.width} {self.height} 255\n".encode()
                ppm_data = ppm_header + raw_frame
                try:
                    image = tk.PhotoImage(data=self.convert_rgb_to_ppm(ppm_data))
                except tk.TclError:
                    # If conversion fails, skip the frame
                    continue

                # Update the canvas
                self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
                self.canvas.image = image  # Keep a reference

                # Wait for the next frame
                time.sleep(delay)
        except Exception as e:
            print(f"Error during video playback: {e}")
        finally:
            self.video_process.stdout.close()
            self.video_process.terminate()
            self.video_process = None
            self.stop_event.set()
            self.cleanup()

    def convert_rgb_to_ppm(self, ppm_data):
        """
        Converts raw RGB data to base64-encoded PPM for PhotoImage.
        """
        import base64
        return base64.b64encode(ppm_data)

    def stop_video(self):
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.stop_event.set()

        # Stop audio
        winsound.PlaySound(None, winsound.SND_PURGE)

        # Terminate video process
        if self.video_process:
            self.video_process.terminate()
            self.video_process = None

        # Wait for threads to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join()

        # Clean up temporary audio file
        self.cleanup()

    def cleanup(self):
        if hasattr(self, 'temp_audio'):
            try:
                os.unlink(self.temp_audio.name)
            except Exception:
                pass

    def on_close(self):
        self.stop_video()
        self.master.destroy()

def main():
    root = tk.Tk()
    player = VideoPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
