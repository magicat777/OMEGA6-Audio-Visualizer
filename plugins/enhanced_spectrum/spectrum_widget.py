"""
Enhanced Spectrum Widget
Real-time spectrum analyzer with multiple display modes
"""

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

from src.plugin_base import VisualizationPlugin


class EnhancedSpectrumWidget(VisualizationPlugin):
    """Enhanced spectrum analyzer plugin"""

    PLUGIN_NAME = "Enhanced Spectrum"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Multi-resolution spectrum analyzer with peak hold"

    def __init__(self, parent=None):
        # Initialize settings before parent init
        self.num_bars = 256
        self.min_freq = 20
        self.max_freq = 20000
        self.db_range = 80
        self.db_floor = -80

        # Display modes
        self.show_peak_hold = True
        self.peak_hold_time = 3.0  # seconds
        self.averaging_factor = 0.8

        # Data arrays
        self.spectrum_data = np.zeros(self.num_bars)
        self.peak_data = np.zeros(self.num_bars)
        self.peak_timestamps = np.zeros(self.num_bars)

        # Colors
        self.spectrum_color = (100, 200, 255)  # Light blue
        self.peak_color = (255, 100, 100)  # Light red

        super().__init__(parent)

    def _init_visualization(self):
        """Initialize spectrum visualization"""
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("k")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Configure axes
        self.plot_widget.setLabel("left", "Level", units="dB")
        self.plot_widget.setLabel("bottom", "Frequency", units="Hz")
        # Y-axis from 0 to db_range for positive bar heights
        self.plot_widget.setYRange(0, self.db_range)
        self.plot_widget.setXRange(np.log10(self.min_freq), np.log10(self.max_freq))
        
        # Set custom tick labels for frequency axis
        x_ticks = []
        for freq in [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
            if self.min_freq <= freq <= self.max_freq:
                x_ticks.append((np.log10(freq), str(freq)))
        self.plot_widget.getAxis('bottom').setTicks([x_ticks])

        # Create bar items
        self.create_frequency_bins()

        # Main spectrum bars - initialize with zeros (will be updated when data arrives)
        self.spectrum_bars = pg.BarGraphItem(
            x=self.bar_positions,
            height=np.zeros_like(self.bar_positions),
            width=self.bar_widths,
            brush=self.spectrum_color,
            pen=None,
            y0=0  # Base at 0
        )
        self.plot_widget.addItem(self.spectrum_bars)

        # Peak hold bars
        self.peak_bars = pg.BarGraphItem(
            x=self.bar_positions,
            height=np.zeros_like(self.bar_positions),
            width=self.bar_widths,
            brush=self.peak_color,
            pen=None,
            y0=0  # Base at 0
        )
        self.plot_widget.addItem(self.peak_bars)

        # Add to layout
        self.content_layout.addWidget(self.plot_widget)

        # Add controls
        self._create_controls()

    def create_frequency_bins(self):
        """Create logarithmically spaced frequency bins"""
        # Create log-spaced frequencies
        log_min = np.log10(self.min_freq)
        log_max = np.log10(self.max_freq)

        # Bin edges
        bin_edges = np.logspace(log_min, log_max, self.num_bars + 1)

        # Calculate positions and widths for bars
        self.frequencies = (bin_edges[:-1] + bin_edges[1:]) / 2
        self.bar_positions = np.log10(self.frequencies)
        self.bar_widths = np.diff(np.log10(bin_edges))

        # Store bin edges for FFT mapping
        self.bin_edges = bin_edges

    def _create_controls(self):
        """Create control panel"""
        controls = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        # Peak hold toggle
        self.peak_toggle = QtWidgets.QPushButton("Peak Hold: ON")
        self.peak_toggle.setCheckable(True)
        self.peak_toggle.setChecked(True)
        self.peak_toggle.clicked.connect(self._toggle_peak_hold)
        layout.addWidget(self.peak_toggle)

        # Reset peaks button
        reset_btn = QtWidgets.QPushButton("Reset Peaks")
        reset_btn.clicked.connect(self._reset_peaks)
        layout.addWidget(reset_btn)

        # Bar count selector
        layout.addWidget(QtWidgets.QLabel("Bars:"))
        self.bar_selector = QtWidgets.QComboBox()
        self.bar_selector.addItems(["64", "128", "256", "512", "1024"])
        self.bar_selector.setCurrentText(str(self.num_bars))
        self.bar_selector.currentTextChanged.connect(self._change_bar_count)
        layout.addWidget(self.bar_selector)

        # Range selector
        layout.addWidget(QtWidgets.QLabel("Range:"))
        self.range_selector = QtWidgets.QComboBox()
        self.range_selector.addItems(["60 dB", "80 dB", "100 dB", "120 dB"])
        self.range_selector.setCurrentText(f"{self.db_range} dB")
        self.range_selector.currentTextChanged.connect(self._change_range)
        layout.addWidget(self.range_selector)

        layout.addStretch()
        controls.setLayout(layout)
        self.content_layout.addWidget(controls)

    def _toggle_peak_hold(self):
        """Toggle peak hold display"""
        self.show_peak_hold = self.peak_toggle.isChecked()
        self.peak_toggle.setText(f"Peak Hold: {'ON' if self.show_peak_hold else 'OFF'}")
        self.peak_bars.setVisible(self.show_peak_hold)

        if not self.show_peak_hold:
            self._reset_peaks()

    def _reset_peaks(self):
        """Reset peak hold values"""
        self.peak_data.fill(self.db_floor)
        self.peak_timestamps.fill(0)
        self._update_display()

    def _change_bar_count(self, text: str):
        """Change number of spectrum bars"""
        try:
            new_count = int(text)
            if new_count != self.num_bars:
                self.num_bars = new_count
                self.spectrum_data = np.zeros(self.num_bars)
                self.peak_data = np.zeros(self.num_bars)
                self.peak_timestamps = np.zeros(self.num_bars)

                # Recreate frequency bins
                self.create_frequency_bins()

                # Update bar items
                self.plot_widget.removeItem(self.spectrum_bars)
                self.plot_widget.removeItem(self.peak_bars)

                self.spectrum_bars = pg.BarGraphItem(
                    x=self.bar_positions,
                    height=self.spectrum_data,
                    width=self.bar_widths,
                    brush=self.spectrum_color,
                    pen=None,
                )
                self.plot_widget.addItem(self.spectrum_bars)

                self.peak_bars = pg.BarGraphItem(
                    x=self.bar_positions,
                    height=self.peak_data,
                    width=self.bar_widths,
                    brush=self.peak_color,
                    pen=None,
                )
                self.plot_widget.addItem(self.peak_bars)

        except ValueError:
            pass

    def _change_range(self, text: str):
        """Change dB range"""
        try:
            self.db_range = int(text.split()[0])
            self.db_floor = -self.db_range
            self.plot_widget.setYRange(self.db_floor, 0)
        except ValueError:
            pass

    def process_audio(self, audio_data: np.ndarray, sample_rate: int):
        """Process audio data (not used for spectrum)"""
        # Unused parameters for this plugin
        _ = (audio_data, sample_rate)

    def process_fft(self, fft_data: np.ndarray, frequencies: np.ndarray):
        """Process FFT data to update spectrum"""
        if fft_data.size == 0:
            return

        # Debug: Log that we're receiving FFT data
        if not hasattr(self, '_fft_count'):
            self._fft_count = 0
        self._fft_count += 1
        
        if self._fft_count % 50 == 0:
            max_val = np.max(fft_data)
            self.logger.info(f"Enhanced Spectrum: FFT data size: {fft_data.shape}, max: {max_val:.2f}")
            if self._fft_count == 50:  # Log frequency range once
                self.logger.info(f"Frequency range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz")

        # Convert to dB
        magnitude = np.abs(fft_data)
        db_data = 20 * np.log10(np.maximum(magnitude, 1e-10))

        # Map FFT bins to display bars
        new_spectrum = np.full(self.num_bars, self.db_floor)

        for i in range(self.num_bars):
            # Find FFT bins in this frequency range
            freq_mask = (frequencies >= self.bin_edges[i]) & (frequencies < self.bin_edges[i + 1])

            if np.any(freq_mask):
                # Use maximum value in bin
                new_spectrum[i] = np.max(db_data[freq_mask])

        # Apply averaging
        self.spectrum_data = (
            self.averaging_factor * self.spectrum_data + (1 - self.averaging_factor) * new_spectrum
        )

        # Update peak hold
        if self.show_peak_hold:
            current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay() / 1000.0

            # Update peaks where current value exceeds
            peak_mask = self.spectrum_data > self.peak_data
            self.peak_data[peak_mask] = self.spectrum_data[peak_mask]
            self.peak_timestamps[peak_mask] = current_time

            # Decay old peaks
            old_peaks = (current_time - self.peak_timestamps) > self.peak_hold_time
            decay_rate = 0.95  # Decay factor per update
            self.peak_data[old_peaks] *= decay_rate

            # Ensure peaks don't go below current spectrum
            self.peak_data = np.maximum(self.peak_data, self.spectrum_data)

        # Update display
        self._update_display()

    def _update_display(self):
        """Update the spectrum display"""
        # Ensure data doesn't exceed floor
        display_spectrum = np.maximum(self.spectrum_data, self.db_floor)
        display_peaks = np.maximum(self.peak_data, self.db_floor)

        # Convert from dB to linear scale for display (0 to db_range)
        # spectrum_data is in dB (negative values), convert to positive height
        spectrum_heights = display_spectrum - self.db_floor  # This gives 0 to db_range
        peak_heights = display_peaks - self.db_floor
        
        # Debug occasional updates
        if hasattr(self, '_update_count'):
            self._update_count += 1
        else:
            self._update_count = 0
            
        if self._update_count % 100 == 0:
            non_zero = np.sum(spectrum_heights > 1)  # Count bars above 1 dB
            if non_zero > 0:
                self.logger.info(f"Spectrum update: {non_zero} bars active, max height: {np.max(spectrum_heights):.1f}")
        
        # Update the actual bar data
        self.spectrum_bars.setOpts(height=spectrum_heights)

        if self.show_peak_hold:
            self.peak_bars.setOpts(height=peak_heights)

    def _update_visualization_size(self):
        """Handle resize events"""
        # PyQtGraph handles this automatically
        pass
