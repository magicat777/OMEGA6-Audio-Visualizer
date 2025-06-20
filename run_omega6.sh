#!/bin/bash
# Run OMEGA6 with proper environment

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Export any needed environment variables
export QT_QPA_PLATFORM=xcb
export PYTHONUNBUFFERED=1

# Log device info first
echo "Audio Devices Available:"
python -c "from src.audio_manager import AudioManager; m = AudioManager(); print(m.list_devices_info())"
echo ""
echo "Starting OMEGA6..."

# Run OMEGA6
python omega6_main.py