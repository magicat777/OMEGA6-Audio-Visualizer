#!/usr/bin/env python3
"""Debug audio capture to check if we're getting data"""

import sounddevice as sd
import numpy as np
import time

def find_pipewire_device():
    """Find the PipeWire device index"""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if 'pipewire' in device['name'].lower():
            return idx, device
    return None, None

def test_audio_capture():
    """Test audio capture from PipeWire"""
    pw_idx, pw_device = find_pipewire_device()
    
    if pw_idx is None:
        print("❌ PipeWire device not found!")
        return
        
    print(f"✅ Found PipeWire device at index {pw_idx}: {pw_device['name']}")
    print(f"   Channels: {pw_device['max_input_channels']} in, {pw_device['max_output_channels']} out")
    print(f"   Sample rate: {pw_device['default_samplerate']} Hz")
    
    print("\n🎵 Testing audio capture for 5 seconds...")
    print("   (Play some music through your Scarlett 2i2)")
    
    # Capture audio
    duration = 5
    sample_rate = int(pw_device['default_samplerate'])
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"⚠️  Status: {status}")
        
        # Calculate level
        level = np.max(np.abs(indata))
        level_db = 20 * np.log10(max(level, 1e-10))
        
        # Print level meter
        bar_length = int((level_db + 60) / 60 * 40)  # Scale -60 to 0 dB
        bar = "=" * max(0, bar_length)
        print(f"\r Level: {level_db:6.1f} dB [{bar:<40}]", end="", flush=True)
    
    # Start stream
    with sd.InputStream(device=pw_idx, channels=2, samplerate=sample_rate, 
                       callback=audio_callback):
        print("\n")
        time.sleep(duration)
    
    print("\n\n✅ Test complete!")
    
    # Check default device
    print("\n📋 Current audio setup:")
    print(f"   Default input device: {sd.default.device[0]}")
    print(f"   Default output device: {sd.default.device[1]}")
    
    # Suggest fix if needed
    if sd.default.device[0] != pw_idx:
        print(f"\n⚠️  Default input is not PipeWire (it's device {sd.default.device[0]})")
        print(f"   To fix: sd.default.device = ({pw_idx}, sd.default.device[1])")

if __name__ == "__main__":
    test_audio_capture()