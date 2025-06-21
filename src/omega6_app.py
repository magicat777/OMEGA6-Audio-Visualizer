"""
OMEGA6 Main Application
Extends Friture with custom plugins and features
"""

import logging

import numpy as np
from PyQt5 import QtCore, QtWidgets

# Import Friture components
try:
    from friture.audiobackend import AudioBackend  # noqa: F401
except ImportError as e:
    logging.error(f"Failed to import Friture components: {e}")
    # Fallback imports or stubs
    AudioBackend = None

from .audio_manager import AudioManager
from .plugin_manager import PluginManager


class OMEGA6App(QtWidgets.QMainWindow):
    """Main OMEGA6 application window"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Initialize UI
        self.setWindowTitle("OMEGA6 - Professional Audio Visualizer")
        self.setMinimumSize(1600, 900)

        # Set dark theme
        self.setStyleSheet(self._get_dark_style())

        # Initialize audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.register_callback(self._on_audio_data)

        # Initialize plugin manager
        self.plugin_manager = PluginManager()

        # Create UI
        self._create_ui()

        # Load plugins
        self._load_plugins()

        # Setup timers
        self._setup_timers()

        # Restore settings
        self._restore_settings()

    def _get_dark_style(self) -> str:
        """Return dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QDockWidget {
            color: #ffffff;
            font-size: 12px;
        }
        QDockWidget::title {
            background: #2d2d2d;
            padding: 5px;
        }
        QPushButton {
            background-color: #3d3d3d;
            color: white;
            border: 1px solid #5d5d5d;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        QLabel {
            color: #ffffff;
        }
        """

    def _on_audio_data(self, audio_data: np.ndarray, sample_rate: int):
        """Handle incoming audio data"""
        # Debug: Check if we're getting audio
        level = np.max(np.abs(audio_data))
        if hasattr(self, '_audio_count'):
            self._audio_count += 1
        else:
            self._audio_count = 0
            
        if self._audio_count % 50 == 0:  # Log every 50 callbacks
            level_db = 20 * np.log10(max(level, 1e-10))
            self.logger.info(f"Audio received: {level_db:.1f} dB, shape: {audio_data.shape}")
        
        # Calculate FFT
        if audio_data.ndim > 1:
            # Use left channel for FFT
            fft_data = np.fft.rfft(audio_data[:, 0] * np.hanning(len(audio_data)))
        else:
            fft_data = np.fft.rfft(audio_data * np.hanning(len(audio_data)))

        frequencies = np.fft.rfftfreq(len(audio_data), 1 / sample_rate)

        # Update all plugins
        self.plugin_manager.update_all_plugins(
            audio_data=audio_data, fft_data=np.abs(fft_data), frequencies=frequencies
        )

    def _create_ui(self):
        """Create the main UI layout"""
        # Central widget (empty for dock-based layout)
        central = QtWidgets.QWidget()
        central.setMinimumSize(400, 300)
        self.setCentralWidget(central)

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar
        self._create_toolbar()

        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("OMEGA6 Ready")

        # Allow docking on all sides
        self.setDockOptions(
            QtWidgets.QMainWindow.AllowNestedDocks
            | QtWidgets.QMainWindow.AllowTabbedDocks
            | QtWidgets.QMainWindow.AnimatedDocks
        )

    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Add actions
        save_action = QtWidgets.QAction("&Save Layout", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_layout)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QtWidgets.QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        self.view_menu = menubar.addMenu("&View")

        # Plugins menu
        self.plugins_menu = menubar.addMenu("&Plugins")

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QtWidgets.QAction("&About OMEGA6", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """Create main toolbar"""
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setMovable(False)

        # Audio input selector
        input_label = QtWidgets.QLabel(" Audio Input: ")
        self.toolbar.addWidget(input_label)

        self.input_combo = QtWidgets.QComboBox()
        self.input_combo.setMinimumWidth(200)
        # Populate with audio devices
        self._populate_audio_devices()
        self.toolbar.addWidget(self.input_combo)

        self.toolbar.addSeparator()

        # FPS display
        self.fps_label = QtWidgets.QLabel(" FPS: -- ")
        self.toolbar.addWidget(self.fps_label)

    def _populate_audio_devices(self):
        """Populate audio device combo box"""
        self.input_combo.clear()

        # Group by type
        self.input_combo.addItem("--- INPUT DEVICES ---", -1)
        for device in self.audio_manager.get_input_devices():
            icon = "🎤 " if device.is_default else "   "
            display_name = str(device)
            
            # Add note for PipeWire device
            if "pipewire" in device.name.lower():
                display_name += " (All devices routed through PipeWire)"
                
            self.input_combo.addItem(f"{icon}{display_name}", device.index)

        self.input_combo.addItem("--- OUTPUT DEVICES (Monitoring) ---", -1)
        for device in self.audio_manager.get_output_devices():
            icon = "🔊 " if device.is_default else "   "
            self.input_combo.addItem(f"{icon}{device}", device.index)
            
        # Add helpful note
        self.input_combo.addItem("--- NOTE ---", -1)
        self.input_combo.addItem("   Scarlett 2i2 accessible via pipewire device", -1)
        self.input_combo.addItem("   Use pavucontrol or qpwgraph to route audio", -1)

        # Set current device
        if self.audio_manager.current_input_device is not None:
            index = self.input_combo.findData(self.audio_manager.current_input_device)
            if index >= 0:
                self.input_combo.setCurrentIndex(index)

        # Connect change handler
        self.input_combo.currentIndexChanged.connect(self._on_device_changed)

    def _on_device_changed(self, index: int):
        """Handle device selection change"""
        device_index = self.input_combo.currentData()
        if device_index is None or device_index == -1:
            return

        device = self.audio_manager.devices.get(device_index)
        if device:
            if device.is_input:
                self.audio_manager.set_input_device(device_index)
                self.status_bar.showMessage(f"Input device: {device.name}", 3000)
            else:
                # For output devices, we might use them for monitoring
                self.audio_manager.set_output_device(device_index)
                self.status_bar.showMessage(f"Monitoring device: {device.name}", 3000)

    def _load_plugins(self):
        """Load and initialize plugins"""
        # Load built-in Friture widgets first
        self._load_friture_widgets()

        # Load custom OMEGA6 plugins
        self.plugin_manager.discover_plugins()

        for plugin_name, plugin_class in self.plugin_manager.get_plugins().items():
            try:
                self._add_plugin_widget(plugin_name, plugin_class)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def _load_friture_widgets(self):
        """Load built-in Friture widgets"""
        # These would be the actual Friture widgets
        # For now, we'll create placeholders
        default_widgets = [
            ("Spectrum", self._create_spectrum_widget),
            ("Spectrogram", self._create_spectrogram_widget),
            ("Scope", self._create_scope_widget),
            ("Levels", self._create_levels_widget),
        ]

        for name, creator in default_widgets:
            try:
                widget = creator()
                if widget:
                    self._add_dock_widget(name, widget)
            except Exception as e:
                self.logger.error(f"Failed to create {name} widget: {e}")

    def _create_spectrum_widget(self):
        """Create spectrum analyzer widget"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Spectrum Analyzer\n(Friture Built-in)")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(200)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def _create_spectrogram_widget(self):
        """Create spectrogram widget"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Spectrogram\n(Friture Built-in)")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(200)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def _create_scope_widget(self):
        """Create oscilloscope widget"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Oscilloscope\n(Friture Built-in)")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(200)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def _create_levels_widget(self):
        """Create levels meter widget"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Level Meters\n(Friture Built-in)")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(200)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def _add_plugin_widget(self, name: str, plugin_class):
        """Add a plugin widget to the UI"""
        try:
            widget = plugin_class()
            self._add_dock_widget(f"OMEGA6: {name}", widget)
        except Exception as e:
            self.logger.error(f"Failed to create plugin widget {name}: {e}")

    def _add_dock_widget(self, title: str, widget: QtWidgets.QWidget):
        """Add a widget as a dock"""
        dock = QtWidgets.QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
            | QtWidgets.QDockWidget.DockWidgetClosable
        )

        # Add to view menu
        self.view_menu.addAction(dock.toggleViewAction())

        # Add to main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    def _setup_timers(self):
        """Setup update timers"""
        # FPS timer
        self.fps_timer = QtCore.QTimer()
        self.fps_timer.timeout.connect(self._update_fps)
        self.fps_timer.start(1000)  # Update every second

        # Start audio capture
        self.audio_manager.start_capture()

        # Add start/stop action to toolbar
        self._add_audio_controls()

    def _add_audio_controls(self):
        """Add audio control buttons to toolbar"""
        self.toolbar.addSeparator()

        # Start/Stop button
        self.audio_toggle = QtWidgets.QPushButton("⏸ Stop")
        self.audio_toggle.setCheckable(True)
        self.audio_toggle.setChecked(True)
        self.audio_toggle.clicked.connect(self._toggle_audio)
        self.toolbar.addWidget(self.audio_toggle)

        # Refresh devices button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_devices)
        self.toolbar.addWidget(refresh_btn)

        self.toolbar.addSeparator()

        # Level meters
        self.level_label = QtWidgets.QLabel(" L: -∞ dB  R: -∞ dB ")
        self.toolbar.addWidget(self.level_label)

    def _toggle_audio(self):
        """Toggle audio capture"""
        if self.audio_toggle.isChecked():
            self.audio_manager.start_capture()
            self.audio_toggle.setText("⏸ Stop")
            self.status_bar.showMessage("Audio capture started", 2000)
        else:
            self.audio_manager.stop_capture()
            self.audio_toggle.setText("▶ Start")
            self.status_bar.showMessage("Audio capture stopped", 2000)

    def _refresh_devices(self):
        """Refresh audio device list"""
        self.audio_manager.refresh_devices()
        self._populate_audio_devices()
        self.status_bar.showMessage("Audio devices refreshed", 2000)

    def _update_fps(self):
        """Update FPS display"""
        # This would calculate actual FPS
        if hasattr(self, 'fps_label'):
            self.fps_label.setText(" FPS: 60 ")

        # Update audio levels
        if hasattr(self, 'level_label') and self.audio_manager.is_capturing:
            l_db, r_db = self.audio_manager.get_current_level()
            self.level_label.setText(f" L: {l_db:.1f} dB  R: {r_db:.1f} dB ")

    def _save_layout(self):
        """Save current window layout"""
        settings = QtCore.QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self.status_bar.showMessage("Layout saved", 2000)

    def _restore_settings(self):
        """Restore saved settings"""
        settings = QtCore.QSettings()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        state = settings.value("windowState")
        if state:
            self.restoreState(state)

    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About OMEGA6",
            "OMEGA6 Audio Visualizer\n\n"
            "A professional audio visualization system\n"
            "built on top of Friture with custom plugins.\n\n"
            "Version: 1.0.0",
        )

    def closeEvent(self, event):
        """Handle application close"""
        # Save settings
        self._save_layout()

        # Stop audio capture
        self.audio_manager.stop_capture()

        event.accept()
