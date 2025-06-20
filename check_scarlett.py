#!/usr/bin/env python3
"""Check for Scarlett 2i2 using various methods"""

import sounddevice as sd
import subprocess

def check_with_sounddevice():
    """Check all devices with sounddevice"""
    print("=== SOUNDDEVICE CHECK ===")
    devices = sd.query_devices()
    
    # Check if device index 3 exists (from aplay -l output)
    for i in range(20):  # Check more devices
        try:
            device = sd.query_devices(i)
            name = device['name'].lower()
            if 'scarlett' in name or '2i2' in name or 'gen' in name:
                print(f"✓ Found Scarlett at index {i}: {device['name']}")
                print(f"  Channels: {device['max_input_channels']} in, {device['max_output_channels']} out")
        except:
            pass

def check_alsa_devices():
    """Check ALSA devices directly"""
    print("\n=== ALSA DEVICE CHECK ===")
    
    # Get card info
    result = subprocess.run(['cat', '/proc/asound/cards'], capture_output=True, text=True)
    print("Sound cards:")
    print(result.stdout)
    
    # Check for hw:3,0 device (Scarlett)
    print("\nTrying to access Scarlett directly via ALSA...")
    try:
        # Try to query the specific device
        import alsaaudio
        print("alsaaudio module available")
        cards = alsaaudio.cards()
        for card in cards:
            if 'scarlett' in card.lower() or '2i2' in card.lower():
                print(f"✓ Found Scarlett card: {card}")
    except ImportError:
        print("alsaaudio not installed, checking via sounddevice...")
        
def check_pipewire():
    """Check PipeWire devices"""
    print("\n=== PIPEWIRE CHECK ===")
    try:
        result = subprocess.run(['pw-cli', 'list-objects', 'Node'], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if 'scarlett' in line.lower() or '2i2' in line.lower():
                print(f"✓ Found in PipeWire: {line}")
                # Print some context
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    print(f"  {lines[j]}")
    except Exception as e:
        print(f"Could not check PipeWire: {e}")

if __name__ == "__main__":
    check_with_sounddevice()
    check_alsa_devices()
    check_pipewire()
    
    print("\n=== RECOMMENDATION ===")
    print("The Scarlett 2i2 is detected as ALSA card 3.")
    print("You may need to:")
    print("1. Use 'hw:3,0' as the device name")
    print("2. Access it through PipeWire")
    print("3. Check if it's being used by another application")
    print("4. Run 'systemctl --user restart pipewire pipewire-pulse' to restart audio services")