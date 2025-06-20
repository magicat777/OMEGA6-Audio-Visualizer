"""
Studio Meters Widget
Professional audio metering with LUFS, True Peak, and various weightings
"""

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
from PyQt5 import QtCore, QtWidgets

from src.plugin_base import PluginWidget


class StudioMetersWidget(PluginWidget):
    """Professional studio meters plugin"""

    PLUGIN_NAME = "Studio Meters"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Professional audio meters with LUFS, True Peak, and K-weighting"

    def __init__(self, parent=None):
        # Initialize member variables BEFORE calling super().__init__
        # This ensures they exist when _init_plugin is called

        # Metering values
        self.lufs_integrated = -100.0
        self.lufs_short = -100.0
        self.lufs_momentary = -100.0
        self.true_peak_l = -100.0
        self.true_peak_r = -100.0
        self.rms_l = -100.0
        self.rms_r = -100.0

        # Weighting mode
        self.weighting_modes = ["K", "A", "C", "Z"]
        self.current_weighting = 0

        # History for integrated measurements
        self.lufs_history = []
        self.gated = True

        # Now call parent init which will call _init_plugin
        super().__init__(parent)

    def _init_plugin(self):
        """Initialize studio meters UI"""
        # Create meter displays
        self._create_lufs_section()
        self._create_peak_section()
        self._create_controls()

        # Add stretch to push everything up
        self.content_layout.addStretch()

    def _create_lufs_section(self):
        """Create LUFS meters section"""
        group = QtWidgets.QGroupBox("LUFS Meters")
        layout = QtWidgets.QGridLayout()

        # Labels and displays
        meters = [
            ("Integrated:", self._create_meter_display()),
            ("Short-term:", self._create_meter_display()),
            ("Momentary:", self._create_meter_display()),
        ]

        self.lufs_displays = []
        for i, (label, display) in enumerate(meters):
            layout.addWidget(QtWidgets.QLabel(label), i, 0)
            layout.addWidget(display, i, 1)
            self.lufs_displays.append(display)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_peak_section(self):
        """Create peak meters section"""
        group = QtWidgets.QGroupBox("Peak/RMS Meters")
        layout = QtWidgets.QGridLayout()

        # Channel labels
        layout.addWidget(QtWidgets.QLabel("L:"), 0, 0)
        layout.addWidget(QtWidgets.QLabel("R:"), 1, 0)

        # Peak meters
        self.peak_l_bar = self._create_meter_bar()
        self.peak_r_bar = self._create_meter_bar()
        layout.addWidget(self.peak_l_bar, 0, 1)
        layout.addWidget(self.peak_r_bar, 1, 1)

        # Peak values
        self.peak_l_label = QtWidgets.QLabel("-∞ dB")
        self.peak_r_label = QtWidgets.QLabel("-∞ dB")
        layout.addWidget(self.peak_l_label, 0, 2)
        layout.addWidget(self.peak_r_label, 1, 2)

        # True Peak indicators
        self.tp_l_label = QtWidgets.QLabel("TP: -∞")
        self.tp_r_label = QtWidgets.QLabel("TP: -∞")
        self.tp_l_label.setStyleSheet("color: #ff6666;")
        self.tp_r_label.setStyleSheet("color: #ff6666;")
        layout.addWidget(self.tp_l_label, 0, 3)
        layout.addWidget(self.tp_r_label, 1, 3)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_controls(self):
        """Create control buttons"""
        controls = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        # Weighting selector
        weighting_btn = QtWidgets.QPushButton(
            f"Weighting: {self.weighting_modes[self.current_weighting]}"
        )
        weighting_btn.clicked.connect(self._cycle_weighting)
        layout.addWidget(weighting_btn)
        self.weighting_btn = weighting_btn

        # Gating toggle
        gate_btn = QtWidgets.QPushButton("Gated: ON")
        gate_btn.setCheckable(True)
        gate_btn.setChecked(True)
        gate_btn.clicked.connect(self._toggle_gating)
        layout.addWidget(gate_btn)
        self.gate_btn = gate_btn

        # Reset button
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_meters)
        layout.addWidget(reset_btn)

        controls.setLayout(layout)
        self.content_layout.addWidget(controls)

    def _create_meter_display(self) -> QtWidgets.QLabel:
        """Create a meter value display"""
        display = QtWidgets.QLabel("-∞ LUFS")
        display.setStyleSheet(
            """
            QLabel {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: monospace;
                font-size: 16px;
                padding: 5px;
                border: 1px solid #333;
                border-radius: 3px;
            }
        """
        )
        display.setAlignment(QtCore.Qt.AlignRight)
        display.setMinimumWidth(120)
        return display

    def _create_meter_bar(self) -> QtWidgets.QProgressBar:
        """Create a meter bar"""
        bar = QtWidgets.QProgressBar()
        bar.setMinimum(-60)
        bar.setMaximum(0)
        bar.setValue(-60)
        bar.setTextVisible(False)
        bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #333;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ff00, stop: 0.7 #ffff00, stop: 0.9 #ff6600, stop: 1 #ff0000);
            }
        """
        )
        return bar

    def _cycle_weighting(self):
        """Cycle through weighting modes"""
        self.current_weighting = (self.current_weighting + 1) % len(self.weighting_modes)
        self.weighting_btn.setText(f"Weighting: {self.weighting_modes[self.current_weighting]}")
        self.set_status(f"Weighting: {self.weighting_modes[self.current_weighting]}")

    def _toggle_gating(self):
        """Toggle gating on/off"""
        self.gated = self.gate_btn.isChecked()
        self.gate_btn.setText(f"Gated: {'ON' if self.gated else 'OFF'}")
        self._reset_meters()

    def _reset_meters(self):
        """Reset integrated measurements"""
        self.lufs_history.clear()
        self.lufs_integrated = -100.0
        self.set_status("Meters reset")

    def process_audio(self, audio_data: np.ndarray, sample_rate: int):
        """Process audio data for metering"""
        if audio_data.size == 0:
            return

        # Ensure stereo
        if audio_data.ndim == 1:
            audio_data = np.column_stack((audio_data, audio_data))

        # Calculate RMS
        self.rms_l = self._calculate_rms(audio_data[:, 0])
        self.rms_r = self._calculate_rms(
            audio_data[:, 1] if audio_data.shape[1] > 1 else audio_data[:, 0]
        )

        # Calculate True Peak
        self.true_peak_l = self._calculate_true_peak(audio_data[:, 0], sample_rate)
        self.true_peak_r = self._calculate_true_peak(
            audio_data[:, 1] if audio_data.shape[1] > 1 else audio_data[:, 0], sample_rate
        )

        # Calculate LUFS
        self._calculate_lufs(audio_data, sample_rate)

        # Update displays
        self._update_displays()

    def process_fft(self, fft_data: np.ndarray, frequencies: np.ndarray):
        """Not used for metering"""
        # Unused parameters for this plugin
        _ = (fft_data, frequencies)

    def _calculate_rms(self, data: np.ndarray) -> float:
        """Calculate RMS in dB"""
        if data.size == 0:
            return -100.0

        rms = np.sqrt(np.mean(data**2))
        return 20 * np.log10(max(rms, 1e-10))

    def _calculate_true_peak(self, data: np.ndarray, sample_rate: int) -> float:
        """Calculate true peak with oversampling"""
        if data.size == 0:
            return -100.0

        # Simple 4x oversampling for true peak detection
        # In production, use proper upsampling filter
        oversampled = np.interp(
            np.linspace(0, len(data), len(data) * 4), np.arange(len(data)), data
        )

        peak = np.max(np.abs(oversampled))
        return 20 * np.log10(max(peak, 1e-10))

    def _calculate_lufs(self, audio_data: np.ndarray, sample_rate: int):
        """Calculate LUFS values"""
        # Simplified LUFS calculation
        # In production, use pyloudnorm or implement full ITU-R BS.1770-4

        # Apply K-weighting (simplified)
        if self.weighting_modes[self.current_weighting] == "K":
            # Basic K-weighting approximation
            weighted = audio_data * 1.0  # Placeholder
        else:
            weighted = audio_data

        # Calculate power
        power = np.mean(weighted**2, axis=0)
        lufs = -0.691 + 10 * np.log10(np.mean(power) + 1e-10)

        # Update measurements
        self.lufs_momentary = lufs

        # Add to history for integrated measurement
        self.lufs_history.append(lufs)
        if len(self.lufs_history) > sample_rate * 3:  # 3 seconds
            self.lufs_history.pop(0)
            self.lufs_short = np.mean(self.lufs_history)

        # Integrated (gated if enabled)
        if self.gated and len(self.lufs_history) > 10:
            # Simple gating at -70 LUFS
            gated_values = [v for v in self.lufs_history if v > -70]
            if gated_values:
                self.lufs_integrated = np.mean(gated_values)
        elif self.lufs_history:
            self.lufs_integrated = np.mean(self.lufs_history)

    def _update_displays(self):
        """Update all meter displays"""
        # LUFS displays
        self.lufs_displays[0].setText(f"{self.lufs_integrated:.1f} LUFS")
        self.lufs_displays[1].setText(f"{self.lufs_short:.1f} LUFS")
        self.lufs_displays[2].setText(f"{self.lufs_momentary:.1f} LUFS")

        # Peak bars and labels
        self.peak_l_bar.setValue(int(self.rms_l))
        self.peak_r_bar.setValue(int(self.rms_r))
        self.peak_l_label.setText(f"{self.rms_l:.1f} dB")
        self.peak_r_label.setText(f"{self.rms_r:.1f} dB")

        # True peak labels
        self.tp_l_label.setText(f"TP: {self.true_peak_l:.1f}")
        self.tp_r_label.setText(f"TP: {self.true_peak_r:.1f}")

        # Color code true peak warnings
        if self.true_peak_l > -1.0:
            self.tp_l_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        else:
            self.tp_l_label.setStyleSheet("color: #ff6666;")

        if self.true_peak_r > -1.0:
            self.tp_r_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        else:
            self.tp_r_label.setStyleSheet("color: #ff6666;")
