#!/usr/bin/env python3
"""List all audio devices using sounddevice"""

import sounddevice as sd

def list_audio_devices():
    """List all available audio devices with detailed info"""
    print("=== AUDIO DEVICES (via sounddevice) ===\n")
    
    # Get all devices
    devices = sd.query_devices()
    
    print(f"Total devices found: {len(devices)}\n")
    
    # Print detailed info for each device
    for i, device in enumerate(devices):
        name = device['name']
        
        # Check for Focusrite/Scarlett
        focusrite_keywords = ['focusrite', '2i2', 'scarlett', 'usb audio', 'usb-audio']
        is_focusrite = any(keyword in name.lower() for keyword in focusrite_keywords)
        
        if is_focusrite:
            print(f"\n🎤 DEVICE {i}: {name} <-- POSSIBLE FOCUSRITE")
            print("=" * 60)
        else:
            print(f"\nDevice {i}: {name}")
            print("-" * 40)
            
        print(f"  Host API: {device['hostapi']} ({sd.query_hostapis(device['hostapi'])['name']})")
        print(f"  Input channels: {device['max_input_channels']}")
        print(f"  Output channels: {device['max_output_channels']}")
        print(f"  Default sample rate: {device['default_samplerate']} Hz")
        
        # Check if default
        if i == sd.default.device[0]:
            print("  🔹 DEFAULT INPUT DEVICE")
        if i == sd.default.device[1]:
            print("  🔹 DEFAULT OUTPUT DEVICE")
            
    # Also check host APIs
    print("\n\n=== HOST APIs ===")
    try:
        apis = sd.query_hostapis()
        for i, api in enumerate(apis):
            print(f"\n{i}: {api['name']}:")
            print(f"  Default input: {api.get('default_input_device', 'N/A')}")
            print(f"  Default output: {api.get('default_output_device', 'N/A')}")
            print(f"  Devices: {api.get('devices', 'N/A')}")
    except Exception as e:
        print(f"Error querying host APIs: {e}")

if __name__ == "__main__":
    list_audio_devices()
    
    # Also run the sounddevice built-in device list
    print("\n\n=== SOUNDDEVICE QUERY OUTPUT ===")
    print(sd.query_devices())