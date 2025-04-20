#!/usr/bin/env python
"""
Script to manually build wheels for different Python versions.
"""
import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Build wheels for multiple Python versions")
    parser.add_argument(
        "--python-versions",
        type=str,
        default=None,
        help="Comma-separated list of Python versions to build for (e.g. '39,310,311'). "
             "If not specified, builds for the current Python version."
    )
    parser.add_argument(
        "--sdist",
        action="store_true",
        help="Build source distribution instead of wheels"
    )
    return parser.parse_args()


def build_wheels(python_versions=None):
    """Build wheels for the specified Python versions or current version."""
    # Create a wheelhouse directory if it doesn't exist
    wheelhouse = Path("wheelhouse")
    wheelhouse.mkdir(exist_ok=True)
    
    # If no specific versions are provided, use the current Python version
    if not python_versions:
        py_version = f"{sys.version_info.major}{sys.version_info.minor}"
        python_versions = [py_version]
    
    # Set required environment variables
    env = os.environ.copy()
    
    # Build a pattern for all required Python versions
    if len(python_versions) == 1:
        env["CIBW_BUILD"] = f"cp{python_versions[0]}-*"
    else:
        # Build a pattern like "cp39-*,cp310-*,cp311-*"
        version_patterns = [f"cp{ver}-*" for ver in python_versions]
        env["CIBW_BUILD"] = ",".join(version_patterns)
    
    env["CIBW_SKIP"] = "*-musllinux_*"
    env["CIBW_BEFORE_BUILD"] = "pip install cython numpy"
    
    print(f"Building wheels for Python versions: {', '.join(python_versions)} on {platform.system()}")
    
    # Run cibuildwheel
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "cibuildwheel"],
            check=True
        )
        subprocess.run(
            [sys.executable, "-m", "cibuildwheel", "--output-dir", "wheelhouse"],
            env=env,
            check=True
        )
        print(f"Wheels built successfully and available in the 'wheelhouse' directory")
    except subprocess.CalledProcessError as e:
        print(f"Error building wheels: {e}")
        return False
    
    return True


def build_sdist():
    """Build a source distribution package."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "build"],
            check=True
        )
        subprocess.run(
            [sys.executable, "-m", "build", "--sdist"],
            check=True
        )
        print("Source distribution built successfully and available in the 'dist' directory")
    except subprocess.CalledProcessError as e:
        print(f"Error building source distribution: {e}")
        return False
    
    return True


if __name__ == "__main__":
    args = parse_args()
    
    if args.sdist:
        build_sdist()
    else:
        python_versions = None
        if args.python_versions:
            python_versions = args.python_versions.split(',')
        build_wheels(python_versions) 