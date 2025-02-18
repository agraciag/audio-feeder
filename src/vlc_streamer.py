import subprocess
import sys
import os

def stream_media(file_path):
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    if not os.path.exists(vlc_path):
        vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    
    sout = "#transcode{acodec=s16l,channels=2,samplerate=44100}:standard{access=udp,mux=raw,dst=127.0.0.1:12345}"
    
    command = [
        vlc_path,
        file_path,
        "--sout", sout,
        "--play-and-exit",
        "--intf", "dummy"
    ]
    
    try:
        process = subprocess.Popen(command)
        return process
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python vlc_streamer.py <ruta_del_archivo>")
        sys.exit(1)
        
    media_file = sys.argv[1]
    stream_process = stream_media(media_file)
    
    if stream_process:
        try:
            stream_process.wait()
        except KeyboardInterrupt:
            stream_process.terminate()