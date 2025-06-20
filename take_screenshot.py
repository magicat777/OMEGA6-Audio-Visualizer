#!/usr/bin/env python3
"""
Take a screenshot of OMEGA6 for documentation
"""

import os
import subprocess
import time
from datetime import datetime

# Start OMEGA6 in background
print("Starting OMEGA6...")
process = subprocess.Popen(
    ["python", "omega6_main.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

# Wait for it to start
time.sleep(3)

# Take screenshot
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
screenshot_file = f"omega6_screenshot_{timestamp}.png"

print(f"Taking screenshot: {screenshot_file}")
subprocess.run(["gnome-screenshot", "-f", screenshot_file, "-w"])

# Kill the process
process.terminate()
process.wait()

print(f"Screenshot saved: {screenshot_file}")
print(f"File size: {os.path.getsize(screenshot_file) / 1024:.1f} KB")
