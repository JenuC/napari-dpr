import numpy as np
from napari_dpr._widget import enhance_image

# make_napari_viewer is a pytest fixture that returns a napari viewer instance
def test_enhance_image_widget(make_napari_viewer):
    # create a viewer instance
    viewer = make_napari_viewer()
    
    # create a simple test image
    test_image = np.random.random((100, 100)).astype(np.float64)
    
    # add the image to the viewer
    image_layer = viewer.add_image(test_image, name='test_image')
    
    # create our widget with the viewer
    widget = enhance_image()
    
    # Set the widget parameters
    widget.viewer.value = viewer
    widget.image_layer.value = image_layer
    widget.psf.value = 4.0
    widget.gain.value = 2.0
    widget.background.value = 10.0
    
    # call the widget
    widget()
    
    # check that the widget added the two new layers
    assert len(viewer.layers) == 3
    assert 'test_image_DPR_enhanced' in [layer.name for layer in viewer.layers]
    assert 'test_image_magnified' in [layer.name for layer in viewer.layers]
    
    # Test with 3D image
    test_image_3d = np.random.random((100, 100, 5)).astype(np.float64)
    image_layer_3d = viewer.add_image(test_image_3d, name='test_image_3d')
    
    # Update widget
    widget.image_layer.value = image_layer_3d
    
    # call the widget
    widget()
    
    # check that the widget added the two new layers
    assert len(viewer.layers) == 5
    assert 'test_image_3d_DPR_enhanced' in [layer.name for layer in viewer.layers] 