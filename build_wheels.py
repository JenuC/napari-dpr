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
    
    # Get the OS-specific configuration
    system = platform.system().lower()
    if system == 'windows':
        # For Windows, explicitly target the current Python version with the full platform tag
        platform_tags = []
        for py_ver in python_versions:
            # Use the explicit format cp{version}-win_amd64
            platform_tags.append(f"cp{py_ver}-win_amd64")
        
        env["CIBW_BUILD"] = " ".join(platform_tags)
        # No need to skip win32 as we're explicitly selecting win_amd64
        env["CIBW_SKIP"] = "*-musllinux_*"
    else:
        # For Linux/macOS, we can use the standard selectors
        if len(python_versions) == 1:
            env["CIBW_BUILD"] = f"cp{python_versions[0]}-*"
        else:
            version_patterns = [f"cp{ver}-*" for ver in python_versions]
            env["CIBW_BUILD"] = " ".join(version_patterns)
        
        # Skip 32-bit builds and musllinux builds
        env["CIBW_SKIP"] = "*-manylinux_i686 *-musllinux_*"
    
    # Build only for 64-bit architectures
    env["CIBW_ARCHS"] = "auto64"
    env["CIBW_BEFORE_BUILD"] = "pip install cython numpy"
    
    # Debug output
    print(f"Building wheels with:")
    print(f"  CIBW_BUILD: {env.get('CIBW_BUILD', 'not set')}")
    print(f"  CIBW_SKIP: {env.get('CIBW_SKIP', 'not set')}")
    print(f"  CIBW_ARCHS: {env.get('CIBW_ARCHS', 'not set')}")
    print(f"  Python versions: {', '.join(python_versions)}")
    print(f"  Platform: {platform.system()} ({platform.architecture()[0]})")
    
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