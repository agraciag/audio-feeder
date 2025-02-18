# AudioFeeder Project

## Overview
AudioFeeder is a two-part application designed to stream system audio and output it through another instance, with real-time audio level monitoring.

### Components

1. **AudioFeeder App**
   - Video player with basic controls (play/pause/stop)
   - Progress bar for video timeline
   - Captures system audio using Stereo Mix
   - Streams audio over localhost UDP
   - Built with PyQt6

2. **Audio Listener App**
   - Receives audio stream from AudioFeeder
   - Displays real-time audio levels
   - Shows peak levels
   - Will be expanded for captioning capabilities

## Current Status
- Both applications communicate via UDP on localhost (Port 12345)
- Basic video playback controls implemented
- Real-time audio level visualization working
- System audio capture using Stereo Mix
- Audio streaming in stereo format

## Technical Stack
- Python 3.11
- PyQt6
- pyaudio
- numpy

## Prerequisites
- Windows OS
- Stereo Mix enabled in Windows sound settings

## Setup
```bash
conda create -n audiofeed python=3.11
conda activate audiofeed
conda install numpy
conda install portaudio
pip install pyaudio PyQt6
```

## Running the Applications
1. Enable Stereo Mix in Windows sound settings
2. Start AudioFeeder:
```bash
python audiofeeder.py
```
3. Start Audio Listener:
```bash
python audio_listener.py
```

## Next Steps
- Improve audio synchronization
- Add support for multiple audio formats
- Implement error handling for network issues
- Add speech-to-text processing
- Implement audio recording capability