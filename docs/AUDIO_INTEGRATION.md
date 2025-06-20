# OMEGA6 Audio Integration

## Overview
OMEGA6 has full audio device support with PipeWire/JACK integration, allowing seamless routing of audio between applications.

## Audio Architecture

### Device Enumeration
- Supports ALL audio devices (input and output)
- Automatic detection of PipeWire devices
- Real-time device switching
- Low-latency capture (10.7ms)

### PipeWire Integration
```
Found devices:
- pipewire (Input/Output, 64ch, 44100.0Hz)
- Multiple ALSA devices via PipeWire
- Virtual sinks/sources supported
- JACK compatibility built-in
```

### Audio Manager Features
1. **Comprehensive Device List**
   - Input devices (microphones, line-in)
   - Output devices (speakers, headphones)
   - Virtual devices (PipeWire/JACK)
   - Default device detection

2. **Real-time Capture**
   - 48kHz sample rate
   - 512 sample chunks (10.7ms latency)
   - Stereo or mono support
   - Thread-safe processing

3. **Audio Routing**
   - Works with QJackCTL
   - PipeWire patchbay compatible
   - Can receive from any PipeWire source
   - Can monitor any output

## Usage

### Basic Operation
1. Select audio device from dropdown
2. Audio capture starts automatically
3. Real-time level meters show activity
4. All plugins receive audio/FFT data

### Advanced Routing with QJackCTL
```bash
# Start QJackCTL
qjackctl

# In QJackCTL Graph:
# - Find "OMEGA6" client
# - Connect any audio source to OMEGA6 input
# - Route from DAWs, media players, etc.
```

### PipeWire Commands
```bash
# List all audio nodes
pw-cli list-objects | grep media.class

# Create virtual sink for OMEGA6
pactl load-module module-null-sink sink_name=omega6_sink

# Route application to OMEGA6
pw-link "Firefox:output_FL" "OMEGA6:input_0"
```

## Plugins Using Audio

### Studio Meters
- LUFS measurement
- True Peak detection
- RMS levels
- K/A/C weighting

### Enhanced Spectrum
- 256-bar spectrum analyzer
- Logarithmic frequency scale
- Peak hold with decay
- Adjustable range

### Voice Detection (Coming Soon)
- Real-time voice activity
- Confidence meters
- Classification

## Performance

- **Latency**: 10.7ms (512 samples @ 48kHz)
- **CPU Usage**: <5% for audio capture
- **Memory**: Minimal (~10MB for buffers)
- **Threading**: Separate audio thread

## Troubleshooting

### No Audio Input
1. Check device selection
2. Verify PipeWire is running: `systemctl --user status pipewire`
3. Check levels with: `pw-top`

### High Latency
1. Reduce chunk size in AudioManager
2. Use JACK mode: `pw-jack omega6`
3. Adjust PipeWire quantum: `pw-metadata -n settings 0 clock.force-quantum 256`

### Device Not Listed
1. Refresh devices with 🔄 button
2. Check with: `pactl list sources`
3. Restart PipeWire: `systemctl --user restart pipewire`

## Integration Examples

### Route Browser Audio
```bash
# Find browser output
pw-link -o | grep -i chrome

# Connect to OMEGA6
pw-link "Chromium:output_FL" "OMEGA6:input_0"
pw-link "Chromium:output_FR" "OMEGA6:input_1"
```

### Record OMEGA6 Output
```bash
# Create loopback
pactl load-module module-loopback source=omega6.monitor

# Record with any app
```

### Multi-App Mixing
Use QJackCTL Graph view to:
1. Create mixer node
2. Route multiple apps to mixer
3. Route mixer to OMEGA6

## Conclusion

OMEGA6's audio system provides professional-grade capture with the flexibility of PipeWire/JACK routing. The plugin architecture ensures all visualizations receive synchronized audio data with minimal latency.