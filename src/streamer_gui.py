import sys
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                            QFileDialog, QVBoxLayout, QWidget, QLabel)
from PyQt6.QtCore import QThread, pyqtSignal

class StreamThread(QThread):
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.process = None
        
    def run(self):
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if not os.path.exists(vlc_path):
            vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            
        sout = "#transcode{acodec=s16l,channels=2,samplerate=44100}:standard{access=udp,mux=raw,dst=127.0.0.1:12345}"
        
        command = [
            vlc_path,
            self.file_path,
            "--sout", sout,
            "--play-and-exit",
            "--intf", "dummy"
        ]
        
        try:
            self.process = subprocess.Popen(command)
            self.process.wait()
        except Exception as e:
            self.error.emit(str(e))
            
    def stop(self):
        if self.process:
            self.process.terminate()

class StreamerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Media Streamer")
        self.setGeometry(100, 100, 400, 150)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Selecciona un archivo de audio/video")
        
        self.select_button = QPushButton("Seleccionar Archivo")
        self.select_button.clicked.connect(self.select_file)
        
        self.stream_button = QPushButton("Iniciar Streaming")
        self.stream_button.clicked.connect(self.toggle_stream)
        self.stream_button.setEnabled(False)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.stream_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.current_file = None
        self.stream_thread = None
        self.streaming = False
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo",
            "",
            "Media Files (*.mp3 *.mp4 *.avi *.mkv *.mov *.wav *.flac);;All Files (*.*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.status_label.setText(f"Archivo: {os.path.basename(file_path)}")
            self.stream_button.setEnabled(True)
            
    def toggle_stream(self):
        if not self.streaming:
            self.start_stream()
        else:
            self.stop_stream()
            
    def start_stream(self):
        if self.current_file:
            self.stream_thread = StreamThread(self.current_file)
            self.stream_thread.error.connect(self.show_error)
            self.stream_thread.start()
            
            self.streaming = True
            self.stream_button.setText("Detener Streaming")
            self.select_button.setEnabled(False)
            
    def stop_stream(self):
        if self.stream_thread:
            self.stream_thread.stop()
            self.stream_thread.wait()
            
        self.streaming = False
        self.stream_button.setText("Iniciar Streaming")
        self.select_button.setEnabled(True)
            
    def show_error(self, error):
        self.status_label.setText(f"Error: {error}")
        self.stop_stream()
        
    def closeEvent(self, event):
        self.stop_stream()
        event.accept()

def main():
    app = QApplication(sys.argv)
    streamer = StreamerGUI()
    streamer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()