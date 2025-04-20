# run_dpr.py
import numpy as np
import tifffile as tf
from napari_dpr.dpr_core import apply_dpr
import matplotlib.pyplot as plt
import time
#input_image = np.random.rand(64, 64, 5).astype(np.float64)  # example input

input_image = tf.imread(r'test_data\test_image.tif').transpose([1,2,0])
if input_image.ndim == 2:
    input_image = input_image[:, :, np.newaxis]
start = time.time()
dpr_out, magnified = apply_dpr(input_image, psf=4.0)
print(f"Time taken: {time.time() - start:.2f} seconds")
plt.subplot(122)
plt.imshow(dpr_out)
plt.subplot(121)
plt.imshow(magnified.sum(2))
plt.show()