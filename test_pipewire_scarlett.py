#!/usr/bin/env python3
"""Test accessing Scarlett 2i2 through PipeWire"""

import sounddevice as sd
import numpy as np

def test_pipewire_access():
    """Test accessing devices through PipeWire"""
    print("=== Testing PipeWire Audio Access ===\n")
    
    # Find PipeWire device
    devices = sd.query_devices()
    pipewire_idx = None
    
    for idx, device in enumerate(devices):
        if 'pipewire' in device['name'].lower():
            pipewire_idx = idx
            print(f"Found PipeWire at index {idx}:")
            print(f"  Name: {device['name']}")
            print(f"  Channels: {device['max_input_channels']} in, {device['max_output_channels']} out")
            print(f"  Sample rate: {device['default_samplerate']} Hz")
            break
    
    if pipewire_idx is None:
        print("PipeWire device not found!")
        return
        
    print("\n=== PipeWire Audio Routing ===")
    print("With PipeWire, all audio devices (including Scarlett 2i2) are accessible through the PipeWire device.")
    print("You can use tools like:")
    print("  - pw-link: to route audio between devices")
    print("  - qpwgraph: GUI for PipeWire routing")
    print("  - pavucontrol: to select input devices")
    print("  - helvum: another PipeWire patchbay GUI")
    
    print("\n=== To use Scarlett 2i2 in OMEGA6 ===")
    print("1. Select 'pipewire' as the input device in OMEGA6")
    print("2. Use one of these methods to route Scarlett to OMEGA6:")
    print("   a) pavucontrol: Set Scarlett as default input")
    print("   b) qpwgraph: Connect Scarlett outputs to OMEGA6 inputs")
    print("   c) pw-link: Use command line to connect")
    
    print("\n=== Quick Test ===")
    print(f"Testing audio capture from PipeWire (device {pipewire_idx})...")
    
    try:
        # Capture 1 second of audio
        duration = 1
        recording = sd.rec(int(duration * 44100), samplerate=44100, 
                          channels=2, device=pipewire_idx)
        sd.wait()
        
        # Check if we got audio
        level = np.max(np.abs(recording))
        print(f"✓ Successfully captured audio. Peak level: {level:.4f}")
        
        if level < 0.001:
            print("⚠️  No audio detected. Make sure:")
            print("   - Scarlett 2i2 is connected and powered on")
            print("   - Audio is routed through PipeWire")
            print("   - Something is playing/recording through Scarlett")
            
    except Exception as e:
        print(f"✗ Error capturing audio: {e}")

if __name__ == "__main__":
    test_pipewire_access()
    
    print("\n=== Command Line Tools ===")
    print("Check current PipeWire connections:")
    print("  $ pw-link -l")
    print("\nConnect Scarlett to OMEGA6 manually:")
    print("  $ pw-link 'alsa_input.usb-Focusrite_Scarlett_2i2_4th_Gen*:capture_FL' 'OMEGA6:input_FL'")
    print("  $ pw-link 'alsa_input.usb-Focusrite_Scarlett_2i2_4th_Gen*:capture_FR' 'OMEGA6:input_FR'")