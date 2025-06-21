"""
OMEGA6 Audio Manager
Handles audio device enumeration and capture with PipeWire support
"""

import logging
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import sounddevice as sd


@dataclass
class AudioDevice:
    """Audio device information"""

    index: int
    name: str
    channels: int
    sample_rate: float
    is_input: bool
    is_output: bool
    is_default: bool = False
    latency: str = "N/A"

    def __str__(self):
        device_type = []
        if self.is_input:
            device_type.append("Input")
        if self.is_output:
            device_type.append("Output")
        type_str = "/".join(device_type)

        default_str = " [DEFAULT]" if self.is_default else ""
        return f"{self.name} ({type_str}, {self.channels}ch, {self.sample_rate}Hz){default_str}"


class AudioManager:
    """Manages audio devices and capture"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices: Dict[int, AudioDevice] = {}
        self.current_input_device: Optional[int] = None
        self.current_output_device: Optional[int] = None

        # Audio capture state
        self.is_capturing = False
        self.audio_queue = queue.Queue(maxsize=100)
        self.capture_thread: Optional[threading.Thread] = None
        self.stream = None

        # Capture parameters
        self.sample_rate = 48000
        self.chunk_size = 512
        self.channels = 2

        # Callbacks
        self.audio_callbacks: List[Callable] = []

        # Refresh devices on init
        self.refresh_devices()

    def refresh_devices(self) -> Dict[int, AudioDevice]:
        """Refresh and enumerate all audio devices"""
        self.devices.clear()

        try:
            # Get device list from sounddevice
            devices = sd.query_devices()
            # hostapis = sd.query_hostapis()  # Currently unused

            # Get default devices
            default_input = sd.default.device[0]
            default_output = sd.default.device[1]

            self.logger.info(f"Found {len(devices)} audio devices")

            for idx, device in enumerate(devices):
                # Create AudioDevice object
                audio_device = AudioDevice(
                    index=idx,
                    name=device["name"],
                    channels=max(device["max_input_channels"], device["max_output_channels"]),
                    sample_rate=device["default_samplerate"],
                    is_input=device["max_input_channels"] > 0,
                    is_output=device["max_output_channels"] > 0,
                    is_default=(idx == default_input or idx == default_output),
                    latency=f"{device.get('default_low_input_latency', 0)*1000:.1f}ms",
                )

                self.devices[idx] = audio_device

                # Log PipeWire/JACK devices specifically
                if "pipewire" in device["name"].lower() or "jack" in device["name"].lower():
                    self.logger.info(f"Found PipeWire/JACK device: {audio_device}")

            # Set defaults if not already set
            if self.current_input_device is None:
                # Try to find and use PipeWire device by default
                for idx, device in self.devices.items():
                    if "pipewire" in device.name.lower() and device.is_input:
                        self.current_input_device = idx
                        self.logger.info(f"Auto-selected PipeWire device: {device.name}")
                        break
                
                # Fall back to system default if PipeWire not found
                if self.current_input_device is None and default_input is not None:
                    self.current_input_device = default_input
                    
            if self.current_output_device is None and default_output is not None:
                self.current_output_device = default_output

        except Exception as e:
            self.logger.error(f"Error enumerating devices: {e}")

        return self.devices

    def get_input_devices(self) -> List[AudioDevice]:
        """Get all input devices"""
        return [d for d in self.devices.values() if d.is_input]

    def get_output_devices(self) -> List[AudioDevice]:
        """Get all output devices"""
        return [d for d in self.devices.values() if d.is_output]

    def get_all_devices(self) -> List[AudioDevice]:
        """Get all devices (input and output)"""
        return list(self.devices.values())

    def set_input_device(self, device_index: int) -> bool:
        """Set the current input device"""
        if device_index in self.devices and self.devices[device_index].is_input:
            self.current_input_device = device_index
            self.logger.info(f"Set input device to: {self.devices[device_index].name}")

            # Restart capture if running
            if self.is_capturing:
                self.stop_capture()
                self.start_capture()

            return True
        else:
            self.logger.error(f"Invalid input device index: {device_index}")
            return False

    def set_output_device(self, device_index: int) -> bool:
        """Set the current output device (for monitoring)"""
        if device_index in self.devices and self.devices[device_index].is_output:
            self.current_output_device = device_index
            self.logger.info(f"Set output device to: {self.devices[device_index].name}")
            return True
        else:
            self.logger.error(f"Invalid output device index: {device_index}")
            return False

    def start_capture(self) -> bool:
        """Start audio capture"""
        if self.is_capturing:
            self.logger.warning("Capture already running")
            return False

        if self.current_input_device is None:
            self.logger.error("No input device selected")
            return False

        try:
            # Get device info
            device = self.devices[self.current_input_device]

            # Configure stream
            self.stream = sd.InputStream(
                device=self.current_input_device,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                latency="low",
            )

            # Start stream
            self.stream.start()
            self.is_capturing = True

            self.logger.info(f"Started capture from: {device.name}")

            # Start processing thread
            self.capture_thread = threading.Thread(target=self._process_audio_queue)
            self.capture_thread.daemon = True
            self.capture_thread.start()

            return True

        except Exception as e:
            self.logger.error(f"Failed to start capture: {e}")
            return False

    def stop_capture(self):
        """Stop audio capture"""
        if not self.is_capturing:
            return

        self.is_capturing = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.info("Stopped audio capture")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")

        # Put data in queue for processing
        try:
            self.audio_queue.put_nowait(indata.copy())
        except queue.Full:
            # Drop oldest data
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(indata.copy())
            except Exception:
                pass

    def _process_audio_queue(self):
        """Process audio from queue in separate thread"""
        while self.is_capturing:
            try:
                # Get audio data
                audio_data = self.audio_queue.get(timeout=0.1)

                # Call all registered callbacks
                for callback in self.audio_callbacks:
                    try:
                        callback(audio_data, self.sample_rate)
                    except Exception as e:
                        self.logger.error(f"Audio callback error: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")

    def register_callback(self, callback: Callable):
        """Register a callback for audio data"""
        if callback not in self.audio_callbacks:
            self.audio_callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        """Unregister an audio callback"""
        if callback in self.audio_callbacks:
            self.audio_callbacks.remove(callback)

    def get_current_level(self) -> Tuple[float, float]:
        """Get current audio level (L, R) in dB"""
        if not self.is_capturing or self.audio_queue.empty():
            return -100.0, -100.0

        try:
            # Peek at latest data without removing
            audio_data = self.audio_queue.queue[-1]

            # Calculate RMS
            if audio_data.ndim == 1:
                rms = np.sqrt(np.mean(audio_data**2))
                return 20 * np.log10(max(rms, 1e-10)), 20 * np.log10(max(rms, 1e-10))
            else:
                rms_l = np.sqrt(np.mean(audio_data[:, 0] ** 2))
                rms_r = (
                    np.sqrt(np.mean(audio_data[:, 1] ** 2)) if audio_data.shape[1] > 1 else rms_l
                )
                return 20 * np.log10(max(rms_l, 1e-10)), 20 * np.log10(max(rms_r, 1e-10))

        except Exception:
            return -100.0, -100.0

    def list_devices_info(self) -> str:
        """Get formatted device list"""
        info = ["Audio Devices:"]
        info.append("-" * 80)

        # Input devices
        info.append("\nINPUT DEVICES:")
        for device in self.get_input_devices():
            marker = " -> " if device.index == self.current_input_device else "    "
            info.append(f"{marker}[{device.index}] {device}")

        # Output devices
        info.append("\nOUTPUT DEVICES:")
        for device in self.get_output_devices():
            marker = " -> " if device.index == self.current_output_device else "    "
            info.append(f"{marker}[{device.index}] {device}")

        # Current settings
        info.append("\nCURRENT SETTINGS:")
        info.append(f"Sample Rate: {self.sample_rate} Hz")
        info.append(f"Chunk Size: {self.chunk_size} samples")
        info.append(f"Channels: {self.channels}")
        info.append(f"Latency: {self.chunk_size / self.sample_rate * 1000:.1f} ms")

        return "\n".join(info)
