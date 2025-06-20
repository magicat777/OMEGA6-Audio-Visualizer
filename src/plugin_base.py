"""
Base class for OMEGA6 plugins
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Dict

import numpy as np
from PyQt5 import QtCore, QtWidgets


# Create a metaclass that combines Qt's metaclass with ABC
class PluginMeta(type(QtWidgets.QWidget), ABCMeta):
    pass


class PluginWidget(QtWidgets.QWidget, metaclass=PluginMeta):
    """Base class for all OMEGA6 plugin widgets"""

    # Plugin metadata
    PLUGIN_NAME = "Base Plugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Base plugin class"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f"{__name__}.{self.PLUGIN_NAME}")

        # Audio data
        self.sample_rate = 48000
        self.fft_size = 2048
        self.audio_data = None
        self.fft_data = None

        # Update rate control
        self.update_interval = 50  # ms
        self.last_update = 0

        # Initialize UI
        self._init_ui()

        # Initialize plugin
        self._init_plugin()

    def _init_ui(self):
        """Initialize base UI layout"""
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Add title label
        self.title_label = QtWidgets.QLabel(self.PLUGIN_NAME)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #2d2d2d;
                border-radius: 3px;
            }
        """
        )
        self.layout.addWidget(self.title_label)

        # Plugin content area
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.layout.addWidget(self.content_widget)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 10px;
                color: #888;
                padding: 2px;
            }
        """
        )
        self.layout.addWidget(self.status_label)

    @abstractmethod
    def _init_plugin(self):
        """Initialize plugin-specific components"""
        pass

    @abstractmethod
    def process_audio(self, audio_data: np.ndarray, sample_rate: int):
        """Process incoming audio data"""
        pass

    @abstractmethod
    def process_fft(self, fft_data: np.ndarray, frequencies: np.ndarray):
        """Process FFT data"""
        pass

    def update_audio(self, audio_data: np.ndarray, sample_rate: int = 48000):
        """Update with new audio data"""
        self.audio_data = audio_data
        self.sample_rate = sample_rate

        # Check update rate
        current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        if current_time - self.last_update < self.update_interval:
            return

        self.last_update = current_time

        # Process audio
        try:
            self.process_audio(audio_data, sample_rate)
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")

    def update_fft(self, fft_data: np.ndarray, frequencies: np.ndarray):
        """Update with new FFT data"""
        self.fft_data = fft_data

        # Process FFT
        try:
            self.process_fft(fft_data, frequencies)
        except Exception as e:
            self.logger.error(f"Error processing FFT: {e}")

    def set_update_rate(self, fps: int):
        """Set plugin update rate"""
        self.update_interval = int(1000 / fps)

    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings for saving"""
        return {"update_interval": self.update_interval, "enabled": self.isVisible()}

    def load_settings(self, settings: Dict[str, Any]):
        """Load plugin settings"""
        if "update_interval" in settings:
            self.update_interval = settings["update_interval"]
        if "enabled" in settings:
            self.setVisible(settings["enabled"])

    def set_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)


class VisualizationPlugin(PluginWidget):
    """Base class for visualization plugins with canvas"""

    def _init_plugin(self):
        """Initialize visualization components"""
        # Create canvas for drawing
        self.canvas = QtWidgets.QWidget()
        self.canvas.setMinimumHeight(200)
        self.canvas.setStyleSheet("background-color: #000000;")
        self.content_layout.addWidget(self.canvas)

        # Initialize visualization
        self._init_visualization()

    @abstractmethod
    def _init_visualization(self):
        """Initialize visualization-specific components"""
        pass

    def resizeEvent(self, event):
        """Handle widget resize"""
        super().resizeEvent(event)
        # Update visualization size
        self._update_visualization_size()

    def _update_visualization_size(self):
        """Update visualization to match widget size"""
        # Override in subclasses
        pass
