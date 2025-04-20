#!/usr/bin/env python
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np
import sys
import os

# Ensure we're building extensions inplace
if 'build_ext' not in sys.argv:
    sys.argv.append('build_ext')
if '--inplace' not in sys.argv:
    sys.argv.append('--inplace')

# Make sure the compiled .pyd file can be imported from the package
if not os.path.exists("src/napari_dpr"):
    os.makedirs("src/napari_dpr", exist_ok=True)

# Define the extension module - using correct package path
ext_modules = [
    Extension(
        "napari_dpr.dpr_core",  # This will create dpr_core.pyd in the napari_dpr package
        ["src/napari_dpr/dpr_core.pyx"],  # Source file in the napari_dpr package
        include_dirs=[np.get_include()],
        language="c++",
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        extra_compile_args=["-O3"],
    ),
]

setup(
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
    # Ensure the extension is properly placed in the package directory
    package_dir={"": "src"},
    packages=find_packages(where="src"),
) 