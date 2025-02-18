import socket
import pyaudio
import wave
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                            QWidget, QProgressBar)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import sys

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
PORT = 12345

class AudioReceiver(QThread):
    audio_level = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', PORT))

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK)

        while self.running:
            try:
                data, addr = self.socket.recvfrom(CHUNK * 8)
                stream.write(data)
                
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.abs(audio_data).mean()
                self.audio_level.emit(level / 32768.0 * 100)
            except Exception as e:
                print(f"Receiving error: {e}")
                break

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.socket.close()

class AudioListener(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Listener")
        self.setGeometry(100, 100, 400, 200)

        self.status_label = QLabel("Waiting for audio...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.level_meter = QProgressBar()
        self.level_meter.setOrientation(Qt.Orientation.Horizontal)
        self.level_meter.setRange(0, 100)
        self.level_meter.setTextVisible(False)
        
        self.peak_label = QLabel("Peak: 0.0")
        self.peak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.peak = 0.0
        
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.level_meter)
        layout.addWidget(self.peak_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.receiver = AudioReceiver()
        self.receiver.audio_level.connect(self.update_level)
        self.receiver.start()

    def update_level(self, level):
        self.level_meter.setValue(int(level))
        if level > self.peak:
            self.peak = level
            self.peak_label.setText(f"Peak: {self.peak:.1f}")
        self.status_label.setText("Receiving Audio")

    def closeEvent(self, event):
        self.receiver.running = False
        self.receiver.wait(1000)
        self.receiver.terminate()
        event.accept()

def main():
    app = QApplication(sys.argv)
    listener = AudioListener()
    listener.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()