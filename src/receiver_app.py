import socket
import pyaudio
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import sys

CHUNK = 1470  # UDP MTU size
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
PORT = 12345

class VLCReceiver(QThread):
    audio_level = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', PORT))
        
    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK)
        
        while self.running:
            try:
                data, _ = self.socket.recvfrom(CHUNK)
                stream.write(data)
                
                # Calculate audio level
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.abs(audio_data).mean()
                self.audio_level.emit(level / 32768.0 * 100)
            except Exception as e:
                print(f"Error: {e}")
                continue
                
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.socket.close()

class AudioReceiver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Audio Receiver")
        self.setGeometry(100, 100, 400, 150)
        
        # Setup UI
        layout = QVBoxLayout()
        
        self.level_meter = QProgressBar()
        self.level_meter.setOrientation(Qt.Orientation.Horizontal)
        self.level_meter.setRange(0, 100)
        
        self.status_label = QLabel("Waiting for VLC stream...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.level_meter)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Start receiver
        self.receiver = VLCReceiver()
        self.receiver.audio_level.connect(self.update_level)
        self.receiver.start()
        
    def update_level(self, level):
        self.level_meter.setValue(int(level))
        self.status_label.setText("Receiving VLC Stream")
        
    def closeEvent(self, event):
        self.receiver.running = False
        self.receiver.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    receiver = AudioReceiver()
    receiver.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()