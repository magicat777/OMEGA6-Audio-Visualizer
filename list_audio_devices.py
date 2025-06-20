#!/usr/bin/env python3
"""List all audio devices with detailed information"""

import pyaudio

def list_audio_devices():
    """List all available audio devices"""
    p = pyaudio.PyAudio()
    
    print("=== AUDIO DEVICES ===\n")
    
    # Get host API info
    print("Host APIs:")
    for i in range(p.get_host_api_count()):
        info = p.get_host_api_info_by_index(i)
        print(f"  {i}: {info['name']} (devices: {info['deviceCount']})")
    
    print("\nAll Devices:")
    print("-" * 80)
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Check device name for Focusrite
        name = info['name']
        if 'focusrite' in name.lower() or '2i2' in name.lower() or 'scarlett' in name.lower():
            marker = " <-- FOCUSRITE DETECTED"
        else:
            marker = ""
        
        print(f"\nDevice {i}: {name}{marker}")
        print(f"  Host API: {p.get_host_api_info_by_index(info['hostApi'])['name']}")
        print(f"  Channels: {info['maxInputChannels']} in, {info['maxOutputChannels']} out")
        print(f"  Default Sample Rate: {info['defaultSampleRate']} Hz")
        
        if info['maxInputChannels'] > 0:
            print("  Type: INPUT")
        if info['maxOutputChannels'] > 0:
            print("  Type: OUTPUT")
            
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()