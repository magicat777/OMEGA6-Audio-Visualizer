#!/bin/bash
# OMEGA6 Setup Script

echo "OMEGA6 Setup"
echo "============"

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing base requirements..."
pip install numpy scipy PyQt5 pyqtgraph sounddevice

# Try to install Friture
echo ""
echo "Installing Friture..."
if pip install friture; then
    echo "✓ Friture installed successfully"
else
    echo "⚠ Friture installation failed. Trying alternative approach..."
    
    # Clone and install from source as fallback
    if [ ! -d "friture_source" ]; then
        git clone https://github.com/tlecomte/friture.git friture_source
        cd friture_source
        pip install -e .
        cd ..
    fi
fi

# Install additional OMEGA6 requirements
echo ""
echo "Installing OMEGA6 requirements..."
pip install -r requirements.txt || echo "⚠ Some requirements failed to install"

# Test installation
echo ""
echo "Testing OMEGA6..."
python test_omega6.py

echo ""
echo "Setup complete!"
echo ""
echo "To run OMEGA6:"
echo "  source venv/bin/activate"
echo "  python omega6_main.py"
echo ""
echo "To run without Friture (development mode):"
echo "  python test_omega6.py"