"""
Utils Module
============
Utility functions and classes for the IA Hoteles Agent CLI.
"""

from modules.utils.horarios_detector import HorariosDetector
from modules.utils.horarios_detector_playwright import HorariosDetectorPlaywright

__all__ = [
    'HorariosDetector',
    'HorariosDetectorPlaywright',
]
