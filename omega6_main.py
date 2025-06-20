#!/usr/bin/env python3
"""
OMEGA6 - Friture-Based Audio Visualizer
Main application entry point
"""

import logging
import os
import sys

from PyQt5 import QtWidgets

# Add Friture to path if installed locally
try:
    import friture  # noqa: F401
except ImportError:
    print("Installing Friture...")
    os.system("pip install friture")

from src.omega6_app import OMEGA6App


def setup_logging():
    """Configure logging for OMEGA6"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("omega6.log"), logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for OMEGA6"""
    logger = setup_logging()
    logger.info("Starting OMEGA6 Audio Visualizer")

    # Create Qt application
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OMEGA6")
    app.setOrganizationName("AudioVisualizer")

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    try:
        omega6 = OMEGA6App()
        omega6.show()

        logger.info("OMEGA6 initialized successfully")

        # Run application
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"Failed to start OMEGA6: {e}", exc_info=True)
        QtWidgets.QMessageBox.critical(
            None, "OMEGA6 Error", f"Failed to start application:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
