# run_dpr.py
import os
import numpy as np
import tifffile as tf
from napari_dpr.dpr_core import apply_dpr
import matplotlib.pyplot as plt
import time
from pathlib import Path

def run_example(input_file=None):
    """Run DPR on an example image file."""
    
    # If no input file is provided, try to find the test image in standard locations
    if input_file is None:
        # Try several possible locations for the test image
        possible_paths = [
            "test_data/test_image.tif",            # Repository structure
            "../test_data/test_image.tif",         # If run from src directory
            "../../test_data/test_image.tif",      # If run from deeper directory
            os.path.join(os.path.dirname(__file__), '../../test_data/test_image.tif')  # Relative to script
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                input_file = path
                break
        
        if input_file is None:
            # If no test image is found, generate a random one
            print("No test image found, generating random data...")
            input_image = np.random.rand(64, 64, 5).astype(np.float64)
        else:
            print(f"Using test image: {input_file}")
    else:
        print(f"Using provided image: {input_file}")
    
    # Load the image if a file was found or provided
    if input_file is not None:
        input_image = tf.imread(input_file)
        # Ensure correct dimensions (HEIGHT, WIDTH, TIME)
        if input_image.ndim == 3 and input_image.shape[0] < input_image.shape[1]:
            input_image = input_image.transpose([1, 2, 0])
    
    # Ensure 3D image (HEIGHT, WIDTH, TIME)
    if input_image.ndim == 2:
        input_image = input_image[:, :, np.newaxis]
    
    # Process with DPR
    print(f"Processing image of shape {input_image.shape}...")
    start = time.time()
    dpr_out, magnified = apply_dpr(input_image, psf=4.0)
    print(f"Time taken: {time.time() - start:.2f} seconds")
    
    # Display results
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.title("Original (Magnified)")
    plt.imshow(magnified.sum(2))
    plt.subplot(122)
    plt.title("DPR Enhanced")
    plt.imshow(dpr_out)
    plt.tight_layout()
    plt.show()
    
    return dpr_out, magnified

if __name__ == "__main__":
    run_example()