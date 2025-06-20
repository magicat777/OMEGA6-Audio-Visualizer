#!/bin/bash
# Run OMEGA6 and take a screenshot after it starts

source venv/bin/activate

# Run OMEGA6 in background
python omega6_main.py &
OMEGA_PID=$!

# Wait for window to appear
sleep 3

# Take screenshot using gnome-screenshot
gnome-screenshot -w -f omega6_screenshot.png 2>/dev/null || \
scrot -s omega6_screenshot.png 2>/dev/null || \
import -window root omega6_screenshot.png 2>/dev/null || \
echo "No screenshot tool available"

# Keep running for a bit
sleep 5

# Kill the process
kill $OMEGA_PID 2>/dev/null

echo "Screenshot saved as omega6_screenshot.png (if available)"