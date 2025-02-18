# AudioFeeder

Real-time audio streaming and monitoring system with video playback capabilities.

## Features
- System audio capture via Stereo Mix
- Video playback with controls
- Real-time audio level visualization
- UDP streaming over localhost
- Peak audio level monitoring

## Prerequisites
- Windows OS with Stereo Mix enabled
- Python 3.11
- VLC Media Player

## Installation
```bash
# Create conda environment
conda create -n audiofeed python=3.11
conda activate audiofeed

# Install dependencies
conda install numpy pyaudio
pip install PyQt6

# Copy config
cp config.template.ini config.ini
```

## Configuration
1. Enable Stereo Mix in Windows Sound Settings
2. Update `config.ini` with your VLC path and network settings
3. Set environment variables:
   ```
   AUDIO_PORT=12345
   AUDIO_HOST=127.0.0.1
   ```

## Usage
1. Start the audio receiver:
```bash
python src/audio_listener.py
```

2. Start AudioFeeder:
```bash
python src/audio_feeder.py
```

## Development
- Fork the repository
- Create feature branch (`git checkout -b feature/name`)
- Commit changes (`git commit -am 'Add feature'`)
- Push branch (`git push origin feature/name`)
- Create Pull Request

## Security
- Never commit `config.ini` or `.env` files
- Use environment variables for sensitive data
- Review code for hardcoded credentials before commits

## License
MIT License

## Contributors
Jokin Cuadrado, Alejandro Gracia