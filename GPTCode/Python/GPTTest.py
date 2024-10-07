import sys
import av
import numpy as np
import threading
import time
from collections import deque

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QImage, QPixmap

import pyaudio

class FrameData:
    def __init__(self, image: np.ndarray, pts: float):
        self.image = image
        self.pts = pts  # Presentation timestamp in seconds

class AudioPlayer:
    def __init__(self, format, channels, rate):
        self.p = pyaudio.PyAudio()
        try:
            self.stream = self.p.open(format=format,
                                      channels=channels,
                                      rate=rate,
                                      output=True,
                                      frames_per_buffer=1024)
        except Exception as e:
            raise RuntimeError(f"Failed to open audio stream: {e}")
        self.lock = threading.Lock()
        self.buffer = deque()
        self.playing = False
        self.thread = None

    def add_frames(self, data):
        with self.lock:
            self.buffer.append(data)

    def play(self):
        if not self.playing:
            self.playing = True
            self.thread = threading.Thread(target=self._playback, daemon=True)
            self.thread.start()

    def _playback(self):
        while self.playing:
            with self.lock:
                if self.buffer:
                    data = self.buffer.popleft()
                else:
                    data = None
            if data:
                try:
                    self.stream.write(data)
                except Exception as e:
                    print(f"Audio playback error: {e}")
            else:
                time.sleep(0.01)  # Avoid busy waiting

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except Exception as e:
            print(f"Error closing audio stream: {e}")

class FrameDecoder(QThread):
    frame_decoded = pyqtSignal(FrameData)
    audio_decoded = pyqtSignal(bytes)
    video_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._running = True

    def run(self):
        try:
            container = av.open(self.file_path)
            stream_video = container.streams.video[0] if container.streams.video else None
            stream_audio = container.streams.audio[0] if container.streams.audio else None

            if not stream_video:
                self.error_occurred.emit("No video stream found.")
                self.video_finished.emit()
                return

            # Set thread type for better performance
            if stream_video:
                stream_video.thread_type = 'AUTO'
            if stream_audio:
                stream_audio.thread_type = 'AUTO'

            # Time base for video
            time_base_video = stream_video.time_base if stream_video else None

            # Initialize resampler for audio if audio stream exists
            resampler = None
            if stream_audio:
                # Determine audio stream properties
                audio_format = 's16'  # Target format
                audio_layout = 'stereo'  # Target layout
                audio_rate = 44100  # Target sample rate

                # Initialize resampler
                resampler = av.audio.resampler.AudioResampler(
                    format=audio_format,
                    layout=audio_layout,
                    rate=audio_rate
                )

                # Prepare audio parameters
                sample_rate = audio_rate
                channels = 2  # Stereo

                # Initialize audio player
                try:
                    self.audio_player = AudioPlayer(format=pyaudio.paInt16,
                                                    channels=channels,
                                                    rate=sample_rate)
                except RuntimeError as e:
                    self.error_occurred.emit(str(e))
                    self.video_finished.emit()
                    return
            else:
                self.audio_player = None

            # Demux the streams
            for packet in container.demux((stream_video, stream_audio) if stream_audio else (stream_video,)):
                if not self._running:
                    break
                for frame in packet.decode():
                    if not self._running:
                        break
                    if packet.stream.type == 'video':
                        # Handle video frame
                        if frame.pts is None:
                            continue
                        pts = float(frame.pts * time_base_video)
                        img = frame.to_ndarray(format='rgb24')
                        frame_data = FrameData(img, pts)
                        self.frame_decoded.emit(frame_data)
                    elif packet.stream.type == 'audio' and resampler:
                        # Handle audio frame
                        try:
                            # Resample and convert audio frame to desired format
                            resampled_frame = resampler.resample(frame)
                            audio_bytes = resampled_frame.to_bytes()
                            self.audio_decoded.emit(audio_bytes)
                        except Exception as e:
                            self.error_occurred.emit(f"Audio resampling error: {e}")

            # Close the container
            container.close()
            self.video_finished.emit()
        except av.AVError as e:
            self.error_occurred.emit(f"Decoding error: {e}")
            self.video_finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")
            self.video_finished.emit()

    def stop(self):
        self._running = False
        if hasattr(self, 'audio_player') and self.audio_player:
            self.audio_player.stop()
        self.wait()

class VideoPlayer(QWidget):
    update_frame_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python Video Player with Audio")
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Video display label
        self.video_label = QLabel("Load a video to start")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)  # Ensure a minimum size
        self.layout.addWidget(self.video_label)

        # Control buttons
        self.open_button = QPushButton("Open")
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")

        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)

        self.button_layout.addWidget(self.open_button)
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.pause_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # Connections
        self.open_button.clicked.connect(self.open_file)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)

        # Connect update_frame_signal to show_frame
        self.update_frame_signal.connect(self.show_frame)

        # Video variables
        self.decoder_thread = None
        self.frame_queue = deque()
        self.is_playing = False
        self.paused = False
        self.start_time = None
        self.pause_time = None

        # QTimer for frame display
        self.timer = QTimer()
        self.timer.setInterval(10)  # 10 ms interval
        self.timer.timeout.connect(self.display_frames)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            # Stop any existing decoder thread
            if self.decoder_thread and self.decoder_thread.isRunning():
                self.decoder_thread.stop()

            # Clear the frame queue and reset timing
            self.frame_queue.clear()
            self.start_time = None
            self.pause_time = None

            # Start a new decoder thread
            self.decoder_thread = FrameDecoder(file_path)
            self.decoder_thread.frame_decoded.connect(self.enqueue_frame)
            self.decoder_thread.audio_decoded.connect(self.enqueue_audio)
            self.decoder_thread.video_finished.connect(self.on_video_finished)
            self.decoder_thread.error_occurred.connect(self.handle_error)
            self.decoder_thread.start()

            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.is_playing = False
            self.paused = False
            self.video_label.setText("Video loaded. Click Play to start.")

    def enqueue_frame(self, frame_data: FrameData):
        self.frame_queue.append(frame_data)

    def enqueue_audio(self, audio_bytes):
        if self.decoder_thread.audio_player:
            self.decoder_thread.audio_player.add_frames(audio_bytes)

    def play_video(self):
        if not self.decoder_thread:
            return

        if not self.is_playing:
            if self.paused and self.pause_time:
                # Resume playback
                resume_offset = time.time() - self.pause_time
                self.start_time += resume_offset
                if self.decoder_thread.audio_player:
                    self.decoder_thread.audio_player.play()
            else:
                # Start playback
                self.start_time = time.time()
                if self.decoder_thread.audio_player:
                    self.decoder_thread.audio_player.play()

            self.is_playing = True
            self.paused = False
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.timer.start()

    def pause_video(self):
        if self.is_playing:
            self.is_playing = False
            self.paused = True
            self.pause_time = time.time()
            if self.decoder_thread.audio_player:
                self.decoder_thread.audio_player.stop()
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.timer.stop()

    def display_frames(self):
        if not self.is_playing:
            return
        if not self.frame_queue:
            return
        frame = self.frame_queue[0]
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if frame.pts <= elapsed_time:
            frame = self.frame_queue.popleft()
            self.update_frame_signal.emit(frame.image)

    def show_frame(self, frame: np.ndarray):
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(pixmap)
        except Exception as e:
            self.handle_error(f"Error displaying frame: {e}")

    def on_video_finished(self):
        self.is_playing = False
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.video_label.setText("Video finished.")

    def handle_error(self, message):
        self.is_playing = False
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.video_label.setText(f"Error: {message}")
        QMessageBox.critical(self, "Playback Error", message)
        print(f"Error: {message}")

    def closeEvent(self, event):
        if self.decoder_thread and self.decoder_thread.isRunning():
            self.decoder_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
