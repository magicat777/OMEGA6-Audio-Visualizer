#!/usr/bin/env python3
"""
Test script for OMEGA6
Verifies basic functionality without full Friture dependency
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

import logging

import numpy as np
from PyQt5 import QtCore, QtWidgets


def test_plugin_system():
    """Test the plugin system"""
    print("Testing OMEGA6 Plugin System...")

    # Create QApplication first (required for widgets)
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Test plugin manager
    from src.plugin_manager import PluginManager

    pm = PluginManager()
    pm.discover_plugins()

    plugins = pm.get_plugins()
    print(f"\nDiscovered plugins: {list(plugins.keys())}")

    # Test studio meters plugin
    if "Studio Meters" in plugins:
        print("\nTesting Studio Meters plugin...")
        widget = pm.create_plugin_instance("Studio Meters")

        # Test with dummy audio data
        sample_rate = 48000
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Generate test tone (1kHz sine wave)
        frequency = 1000
        amplitude = 0.5
        audio_data = amplitude * np.sin(2 * np.pi * frequency * t)

        # Make stereo
        audio_data = np.column_stack((audio_data, audio_data * 0.8))

        # Process audio
        widget.process_audio(audio_data, sample_rate)

        print("✓ Studio Meters plugin working")

    return True


def test_minimal_ui():
    """Test minimal UI without Friture"""
    print("\nTesting minimal UI...")

    app = QtWidgets.QApplication(sys.argv)

    # Create simple test window
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OMEGA6 Test")
    window.setMinimumSize(800, 600)

    # Add plugin
    from src.plugin_manager import PluginManager

    pm = PluginManager()
    pm.discover_plugins()

    if "Studio Meters" in pm.get_plugins():
        widget = pm.create_plugin_instance("Studio Meters")
        dock = QtWidgets.QDockWidget("Studio Meters", window)
        dock.setWidget(widget)
        window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    window.show()

    # Add timer to close after 2 seconds
    QtCore.QTimer.singleShot(2000, app.quit)

    app.exec_()
    print("✓ UI test completed")

    return True


def main():
    """Run all tests"""
    logging.basicConfig(level=logging.INFO)

    print("OMEGA6 Test Suite")
    print("=" * 50)

    # Test components
    tests = [
        ("Plugin System", test_plugin_system),
        ("Minimal UI", test_minimal_ui),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {name}: {status}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\nAll tests passed! OMEGA6 is ready for development.")
        print("\nNext steps:")
        print("1. Install Friture: pip install friture")
        print("2. Run full application: python omega6_main.py")
    else:
        print("\nSome tests failed. Please check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
