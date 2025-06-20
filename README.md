# OMEGA6 Audio Visualizer

A professional-grade, plugin-based audio visualization system built with Python and Qt5. OMEGA6 provides real-time audio analysis with modular visualization components.

## Features

- **Plugin Architecture**: Modular design allows easy extension with custom visualizations
- **Professional Audio Metering**: LUFS, True Peak, RMS with K-weighting support
- **Multi-Resolution Spectrum Analysis**: Logarithmic frequency bins with peak hold
- **PipeWire Integration**: Comprehensive audio device support with PipeWire/JACK compatibility
- **Real-Time Processing**: Low-latency audio capture and visualization
- **Flexible UI**: Qt5 docking system for customizable layouts

## Installation

### Prerequisites

- Python 3.8+
- PipeWire audio system (for Linux)
- Qt5

### Setup

```bash
# Clone the repository
git clone https://github.com/magicat777/OMEGA6-Audio-Visualizer.git
cd OMEGA6-Audio-Visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run OMEGA6
python omega6_main.py
```

### Controls

- Select audio input device from the dropdown menu
- Enable/disable plugins using the checkboxes
- Drag and dock plugin windows to customize layout
- Each plugin has its own controls for fine-tuning

## Plugins

### Studio Meters
Professional audio metering with:
- LUFS (Integrated, Short-term, Momentary)
- True Peak detection
- RMS levels
- K/A/C/Z weighting modes

### Enhanced Spectrum
Real-time spectrum analyzer featuring:
- Logarithmic frequency scale (20Hz - 20kHz)
- Configurable bar count (64-1024)
- Peak hold with decay
- Adjustable dB range

## Architecture

OMEGA6 uses a modular plugin architecture:

```
OMEGA6/
├── omega6_main.py          # Entry point
├── src/
│   ├── omega6_app.py       # Main application window
│   ├── audio_manager.py    # Audio device management
│   ├── plugin_base.py      # Plugin base classes
│   └── plugin_manager.py   # Plugin discovery and loading
└── plugins/
    ├── studio_meters/      # Professional metering plugin
    └── enhanced_spectrum/  # Spectrum analyzer plugin
```

## Creating Custom Plugins

Extend the `PluginWidget` or `VisualizationPlugin` base class:

```python
from src.plugin_base import VisualizationPlugin

class MyPlugin(VisualizationPlugin):
    PLUGIN_NAME = "My Custom Plugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Description here"
    
    def _init_visualization(self):
        # Initialize your visualization
        pass
    
    def process_audio(self, audio_data, sample_rate):
        # Process raw audio data
        pass
    
    def process_fft(self, fft_data, frequencies):
        # Process FFT data
        pass
```

## Development

### Code Quality

The project maintains high code quality standards:

```bash
# Format code
black .

# Sort imports
isort .

# Run linting
flake8 .

# Type checking
mypy .
```

### Testing

```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_audio_manager.py
```

## Requirements

See `requirements.txt` for full dependencies. Key packages:
- PyQt5
- numpy
- scipy
- pyaudio
- pyqtgraph

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Built as evolution of the OMEGA series audio visualizers
- Inspired by professional audio analysis tools
- Thanks to the PipeWire and Qt communities