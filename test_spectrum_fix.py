#!/usr/bin/env python3
"""Test script to verify spectrum display with simple data"""

import sys
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph as pg

class TestSpectrum(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Spectrum")
        self.resize(800, 600)
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Create plot
        self.plot = pg.PlotWidget()
        self.plot.setBackground('k')
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.plot)
        
        # Test data
        n_bars = 50
        x_pos = np.linspace(0, 5, n_bars)
        widths = np.ones(n_bars) * 0.08
        heights = np.random.rand(n_bars) * 50 + 10
        
        # Create bars
        self.bars = pg.BarGraphItem(
            x=x_pos,
            height=heights,
            width=widths,
            brush='r',
            pen=None
        )
        self.plot.addItem(self.bars)
        
        # Update button
        btn = QtWidgets.QPushButton("Update Bars")
        btn.clicked.connect(self.update_bars)
        layout.addWidget(btn)
        
    def update_bars(self):
        """Update bar heights"""
        n_bars = 50
        new_heights = np.random.rand(n_bars) * 70 + 10
        self.bars.setOpts(height=new_heights)
        print(f"Updated bars with heights: min={new_heights.min():.1f}, max={new_heights.max():.1f}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TestSpectrum()
    window.show()
    sys.exit(app.exec_())