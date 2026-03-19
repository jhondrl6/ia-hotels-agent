"""Pytest configuration for tests.

Adds project root to Python path for imports.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add current directory for data_validation, auditors, etc.
sys.path.insert(0, str(project_root))
