import sys
import pyaudio
import wave
import socket
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QFileDialog, QHBoxLayout, QSlider)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QThread, pyqtSignal, Qt
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
PORT = 12345

class AudioStreamer(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def run(self):
        p = pyaudio.PyAudio()
        
        # Find Stereo Mix device
        stereo_mix_index = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")
            if 'Stereo Mix' in device_info['name'] or 'Mezcla estéreo' in device_info['name']:
                stereo_mix_index = i
                print(f"Found stereo mix device: {device_info['name']}")
                break
        
        if stereo_mix_index is None:
            print("No Stereo Mix device found")
            return
            
        try:
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          input_device_index=stereo_mix_index,
                          frames_per_buffer=CHUNK,
                          stream_callback=None,
                          start=False,
                          input_host_api_specific_stream_info=None)
            
            while self.running:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.socket.sendto(data, ('localhost', PORT))
                except Exception as e:
                    print(f"Streaming error: {e}")
                    break
                    
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error opening stream: {e}")
            
        p.terminate()
        self.socket.close()

class AudioFeeder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AudioFeeder")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.open_button = QPushButton("Open Video")
        self.open_button.clicked.connect(self.open_file)

        self.progress = QSlider(Qt.Orientation.Horizontal)
        self.progress.sliderMoved.connect(self.set_position)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.progress)
        layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.audio_streamer = AudioStreamer()
        self.audio_streamer.start()

        self.is_playing = False

    def play_pause(self):
        if self.is_playing:
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing

    def stop(self):
        self.media_player.stop()
        self.play_button.setText("Play")
        self.is_playing = False

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)"
        )
        
        if filename:
            self.media_player.setSource(QUrl.fromLocalFile(filename))
            self.audio_output.setVolume(1.0)
            self.play_pause()

    def position_changed(self, position):
        self.progress.setValue(position)

    def duration_changed(self, duration):
        self.progress.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def closeEvent(self, event):
        self.audio_streamer.running = False
        self.media_player.stop()
        self.audio_streamer.wait(1000)
        self.audio_streamer.terminate()
        event.accept()

def main():
    app = QApplication(sys.argv)
    player = AudioFeeder()
    player.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()