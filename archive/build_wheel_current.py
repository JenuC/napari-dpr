#!/usr/bin/env python
"""
Simple script to build a wheel for the current Python version only.
This is a simplified approach that doesn't use cibuildwheel.
"""
import os
import sys
import subprocess
from pathlib import Path

def build_wheel_for_current_python():
    """
    Build a wheel for the current Python version using setuptools directly.
    This is simpler than using cibuildwheel for local development.
    """
    print(f"Building wheel for Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Ensure we have the required packages
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools", "cython", "numpy"],
            check=True
        )
        
        # Build the wheel using setup.py
        print("Building wheel...")
        subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace", "bdist_wheel"],
            check=True
        )
        
        print("Wheel built successfully and available in the 'dist' directory")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building wheel: {e}")
        return False

if __name__ == "__main__":
    build_wheel_for_current_python() 