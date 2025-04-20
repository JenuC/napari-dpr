"""
Napari plugin widget for DPR resolution enhancement.
"""
from typing import TYPE_CHECKING
import numpy as np
from magicgui import magic_factory
from napari_dpr.dpr_core import apply_dpr

if TYPE_CHECKING:
    import napari

@magic_factory(
    psf={"widget_type": "FloatSpinBox", "min": 1.0, "max": 10.0, "step": 0.1, "value": 4.0},
    gain={"widget_type": "FloatSpinBox", "min": 0.1, "max": 10.0, "step": 0.1, "value": 2.0},
    background={"widget_type": "FloatSpinBox", "min": 0.0, "max": 50.0, "step": 1.0, "value": 10.0},
    call_button="Enhance Resolution"
)
def enhance_image(
    viewer: "napari.viewer.Viewer",
    image_layer: "napari.layers.Image",
    psf: float = 4.0,
    gain: float = 2.0,
    background: float = 10.0,
) -> None:
    """
    Enhance image resolution using DPR.
    
    Parameters
    ----------
    viewer : napari.viewer.Viewer
        Napari viewer instance
    image_layer : napari.layers.Image
        Input image layer to enhance
    psf : float
        Point spread function size parameter
    gain : float
        Gain parameter for enhancement
    background : float
        Background subtraction value
    """
    if image_layer is None:
        raise ValueError("Please select an image layer")
    
    # Get the image data
    image_data = image_layer.data
    
    # Make sure image has the right dimensions and type
    # DPR expects a 3D array (HEIGHT, WIDTH, TIME/CHANNELS)
    if image_data.ndim == 2:
        # Convert 2D image to 3D with one time point
        image_data = image_data[:, :, np.newaxis]
    elif image_data.ndim == 3 and image_data.shape[0] < image_data.shape[1]:
        # If first dimension is smallest, it's probably [TIME, HEIGHT, WIDTH]
        # We need to transpose to [HEIGHT, WIDTH, TIME]
        image_data = image_data.transpose([1, 2, 0])
    elif image_data.ndim > 3:
        # If 4D or more, take the first 3 dimensions
        image_data = image_data[:, :, :, 0]
        
    # Ensure data is float64
    if image_data.dtype != np.float64:
        image_data = image_data.astype(np.float64)
    
    # Apply DPR
    try:
        dpr_out, magnified = apply_dpr(image_data, psf=psf, gain=gain, background=background)
        

        
        # Add the magnified original for comparison
        viewer.add_image(
            magnified.sum(axis=2),  # Sum over the time/channel dimension
            name=f"{image_layer.name}_magnified",
            colormap=image_layer.colormap.name,
        )

        # Add the enhanced image to the viewer
        viewer.add_image(
            dpr_out,
            name=f"{image_layer.name}_DPR_enhanced",
            colormap=image_layer.colormap.name,
        )
        
    except Exception as e:
        import traceback
        print(f"Error applying DPR: {e}")
        print(traceback.format_exc())
        raise 