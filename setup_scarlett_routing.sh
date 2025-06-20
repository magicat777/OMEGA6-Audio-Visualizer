#!/bin/bash
# Setup Scarlett 2i2 routing for OMEGA6

echo "=== Setting up Scarlett 2i2 Routing for OMEGA6 ==="
echo ""

# Check if Scarlett is connected
if pw-cli list-objects Node | grep -q "Scarlett 2i2"; then
    echo "✓ Scarlett 2i2 detected"
else
    echo "✗ Scarlett 2i2 not detected. Please ensure it's connected and powered on."
    exit 1
fi

# Check available routing tools
if command -v pavucontrol &> /dev/null; then
    echo ""
    echo "Option 1: Using pavucontrol (GUI)"
    echo "  1. Run: pavucontrol"
    echo "  2. Go to 'Recording' tab"
    echo "  3. Find OMEGA6 and set it to use 'Scarlett 2i2 4th Gen Analog Surround 4.0'"
    echo ""
fi

if command -v qpwgraph &> /dev/null; then
    echo "Option 2: Using qpwgraph (GUI)"
    echo "  1. Run: qpwgraph"
    echo "  2. Find 'Scarlett 2i2 4th Gen' outputs"
    echo "  3. Connect them to OMEGA6 inputs"
    echo ""
fi

if command -v helvum &> /dev/null; then
    echo "Option 3: Using helvum (GUI)"
    echo "  1. Run: helvum"
    echo "  2. Connect Scarlett outputs to OMEGA6 inputs"
    echo ""
fi

echo "Option 4: Set Scarlett as default input (Command Line)"
echo "  Running: pactl set-default-source alsa_input.usb-Focusrite_Scarlett_2i2_4th_Gen*"
pactl set-default-source "$(pactl list sources short | grep Scarlett | grep input | awk '{print $2}')" 2>/dev/null && echo "  ✓ Scarlett set as default input" || echo "  ✗ Failed to set default"

echo ""
echo "=== Current Audio Setup ==="
echo "Default input: $(pactl get-default-source)"
echo ""
echo "To verify routing:"
echo "  1. Run OMEGA6"
echo "  2. Select 'pipewire' as input device"
echo "  3. Play/speak into Scarlett inputs"
echo "  4. You should see activity in the meters"