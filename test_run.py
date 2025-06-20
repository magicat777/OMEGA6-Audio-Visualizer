#!/usr/bin/env python3
"""Test script to run OMEGA6 and capture any errors"""

import sys
import subprocess
import time

print("Starting OMEGA6...")
proc = subprocess.Popen(
    [sys.executable, "omega6_main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Let it run for a bit
time.sleep(10)

# Check if still running
if proc.poll() is None:
    print("OMEGA6 is running successfully!")
    print("Process ID:", proc.pid)
    print("\nPress Ctrl+C to stop...")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nStopping OMEGA6...")
else:
    print("OMEGA6 exited with code:", proc.returncode)
    stdout, stderr = proc.communicate()
    if stdout:
        print("\nSTDOUT:")
        print(stdout)
    if stderr:
        print("\nSTDERR:")
        print(stderr)