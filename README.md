# napari-dpr

[![License](https://img.shields.io/pypi/l/napari-dpr.svg?color=green)](https://github.com/jenuc/napari-dpr/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-dpr.svg?color=green)](https://pypi.org/project/napari-dpr)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-dpr.svg?color=green)](https://python.org)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-dpr)](https://napari-hub.org/plugins/napari-dpr)

A napari plugin for image resolution enhancement using Deconvolution by Pixel Reassignment (DPR).

## Description

DPR is a technique for enhancing the resolution of images, particularly useful in microscopy. This plugin provides easy access to DPR functionality within napari, allowing for quick and intuitive image enhancement without leaving your viewer.

The algorithm works by:
1. Applying a specialized deconvolution approach
2. Reassigning pixels based on local information
3. Enhancing fine details while preserving image structure

## Installation

You can install `napari-dpr` via [pip]:

```bash
pip install napari-dpr
```

## Usage

1. Open napari and load an image
2. In the menu, go to `Plugins > DPR Enhancement`
3. Select your image from the dropdown
4. Adjust parameters as needed:
   - **PSF**: Point spread function size (typical values: 2-6)
   - **Gain**: Enhancement gain (typical values: 1-3)
   - **Background**: Background subtraction (typical values: 5-20)
5. Click "Enhance Resolution"
6. Two new layers will be added to your viewer:
   - `[original_name]_DPR_enhanced`: The DPR-enhanced image
   - `[original_name]_magnified`: The magnified original for comparison

## Parameters

- **PSF** (Point Spread Function): Controls the width of the point spread function used in the algorithm. Larger values capture wider spatial correlations but may reduce detail resolution.
- **Gain**: Controls the enhancement strength. Higher values increase contrast but may introduce artifacts.
- **Background**: Controls background subtraction. Higher values remove more background but may affect relevant image features.

## Standalone Usage

You can also use the DPR algorithm programmatically:

```python
from napari_dpr.dpr_core import apply_dpr
import numpy as np
import matplotlib.pyplot as plt

# Load your image data (should be 3D: HEIGHT, WIDTH, TIME)
image_data = your_image_loading_function()
if image_data.ndim == 2:
    image_data = image_data[:, :, np.newaxis]  # Add time dimension if 2D

# Apply DPR
dpr_enhanced, magnified = apply_dpr(image_data, psf=4.0, gain=2.0, background=10.0)

# Visualize results
plt.figure(figsize=(12, 6))
plt.subplot(121)
plt.title("Original (Magnified)")
plt.imshow(magnified.sum(axis=2))
plt.subplot(122)
plt.title("DPR Enhanced")
plt.imshow(dpr_enhanced)
plt.tight_layout()
plt.show()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Distributed under the terms of the [MIT] license,
"napari-dpr" is free and open source software.

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[file an issue]: https://github.com/jenuc/napari-dpr/issues
[napari]: https://github.com/napari/napari
[pip]: https://pypi.org/project/pip/
[MIT]: https://opensource.org/licenses/MIT
