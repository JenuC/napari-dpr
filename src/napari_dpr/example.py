"""
Example script for using napari-dpr programmatically.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import napari
from napari_dpr.dpr_core import apply_dpr
from napari_dpr.run_dpr import run_example

def example_with_test_image():
    """Run an example using the test image or random data if not available."""
    print("Running DPR example with test image...")
    # run_example returns the dpr_out and magnified images
    dpr_out, magnified = run_example()
    print("Done.")

def example_with_napari():
    """Run an example using napari viewer."""
    print("Running DPR example with napari...")
    
    # Create a random test image
    test_image = np.random.random((100, 100, 5)).astype(np.float64)
    
    # Start napari viewer with the test image
    viewer = napari.Viewer()
    viewer.add_image(test_image, name='test_image')
    
    # Process the image with DPR
    dpr_out, magnified = apply_dpr(test_image, psf=4.0)
    
    # Add the processed images to the viewer
    viewer.add_image(dpr_out, name='DPR_enhanced')
    viewer.add_image(magnified.sum(axis=2), name='magnified')
    
    # Start the napari event loop
    napari.run()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--napari':
        example_with_napari()
    else:
        example_with_test_image()
    
    print("To run with napari viewer: python -m napari_dpr.example --napari") 