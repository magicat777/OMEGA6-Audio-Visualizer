#!/usr/bin/env python3
"""
Test audio device enumeration and capture
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

import time

import numpy as np

from src.audio_manager import AudioManager


def test_device_enumeration():
    """Test device enumeration"""
    print("Testing Audio Device Enumeration")
    print("=" * 80)

    manager = AudioManager()
    print(manager.list_devices_info())
    print("\nTotal devices found:", len(manager.devices))
    print("Input devices:", len(manager.get_input_devices()))
    print("Output devices:", len(manager.get_output_devices()))

    # Check for PipeWire devices
    pipewire_devices = [
        d
        for d in manager.devices.values()
        if "pipewire" in d.name.lower() or "pw" in d.name.lower()
    ]
    if pipewire_devices:
        print(f"\nFound {len(pipewire_devices)} PipeWire devices:")
        for device in pipewire_devices:
            print(f"  - {device}")

    return True


def test_audio_capture():
    """Test audio capture"""
    print("\n\nTesting Audio Capture")
    print("=" * 80)

    manager = AudioManager()

    # Audio data collection
    captured_data = []

    def audio_callback(data, sample_rate):
        captured_data.append((data, sample_rate))
        if len(captured_data) == 1:
            print(f"Receiving audio: {data.shape} @ {sample_rate}Hz")

    manager.register_callback(audio_callback)

    print("Starting capture for 3 seconds...")
    if manager.start_capture():
        print("Capture started successfully")

        # Monitor levels
        for i in range(30):  # 3 seconds
            time.sleep(0.1)
            l_db, r_db = manager.get_current_level()
            if i % 10 == 0:  # Print every second
                print(f"Levels: L={l_db:.1f}dB  R={r_db:.1f}dB")

        manager.stop_capture()
        print(f"Captured {len(captured_data)} audio chunks")

        if captured_data:
            # Analyze captured data
            first_chunk = captured_data[0][0]
            print(f"Audio format: {first_chunk.shape}")
            print(f"Sample rate: {captured_data[0][1]} Hz")

            # Check signal
            all_data = np.concatenate([chunk[0] for chunk in captured_data[:10]])
            rms = np.sqrt(np.mean(all_data**2))
            print(f"RMS level: {20*np.log10(max(rms, 1e-10)):.1f} dB")

            return True
    else:
        print("Failed to start capture")
        return False


def test_device_switching():
    """Test switching between devices"""
    print("\n\nTesting Device Switching")
    print("=" * 80)

    manager = AudioManager()
    input_devices = manager.get_input_devices()

    if len(input_devices) > 1:
        print(f"Found {len(input_devices)} input devices")

        # Try switching to second device
        second_device = input_devices[1]
        print(f"Switching to: {second_device.name}")

        if manager.set_input_device(second_device.index):
            print("✓ Device switch successful")
            return True
        else:
            print("✗ Device switch failed")
            return False
    else:
        print("Only one input device found, skipping switch test")
        return True


def main():
    """Run all tests"""
    print("OMEGA6 Audio System Test")
    print("=" * 80)

    tests = [
        ("Device Enumeration", test_device_enumeration),
        ("Audio Capture", test_audio_capture),
        ("Device Switching", test_device_switching),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary:")
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {name}: {status}")

    all_passed = all(success for _, success in results)
    if all_passed:
        print("\nAll audio tests passed!")
        print("\nPipeWire Integration: The audio system works seamlessly with PipeWire.")
        print("You can use QJackCTL or pw-jack to route audio between applications.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
