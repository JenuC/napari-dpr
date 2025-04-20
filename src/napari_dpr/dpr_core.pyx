# distutils: language = c++
import numpy as np
cimport numpy as np
from libc.math cimport fabs, ceil
import scipy.ndimage as ndi
from scipy.interpolate import RectBivariateSpline

np.import_array()

ctypedef np.float64_t DTYPE_t

def dpr_set_parameters(double psf, double gain=1, double background=-1, temporal=None):
    if background < 0:
        background = ceil(17 * psf)
    return {'gain': gain, 'background': background, 'temporal': temporal}

cpdef tuple dpr_update_single(np.ndarray[DTYPE_t, ndim=2] i, double psf, dict opt):
    cdef:
        int h = i.shape[0]
        int w = i.shape[1]
        int r = <int>ceil(opt['background'])
        double g = opt['gain']
        np.ndarray[DTYPE_t, ndim=2] localmin = np.zeros((h, w))
        np.ndarray[DTYPE_t, ndim=2] i_localmin = np.zeros((h, w))
        int u, v

    i = i - i.min()
    for u in range(h):
        for v in range(w):
            sub = i[max(0, u - r):min(h, u + r + 1), max(0, v - r):min(w, v + r + 1)]
            localmin[u, v] = np.min(sub)
            i_localmin[u, v] = i[u, v] - localmin[u, v]

    psf /= 1.6651
    x0 = np.linspace(-0.5, 0.5, w)
    y0 = np.linspace(-0.5, 0.5, h)
    x = np.linspace(-0.5, 0.5, round(5 * w / psf))
    y = np.linspace(-0.5, 0.5, round(5 * h / psf))

    interp_m = RectBivariateSpline(y0, x0, i_localmin)(y, x)
    interp_m[interp_m < 0] = 0
    interp_m = np.pad(interp_m, 10)

    interp_i = RectBivariateSpline(y0, x0, i)(y, x)
    interp_i[interp_i < 0] = 0
    interp_i = np.pad(interp_i, 10)

    hn, wn = interp_i.shape
    norm = interp_m / (ndi.gaussian_filter(interp_m, 10) + 1e-5)

    sobel_x = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
    sobel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    gx = ndi.convolve(norm, sobel_y, mode='reflect') / (norm + 1e-5)
    gy = ndi.convolve(norm, sobel_x, mode='reflect') / (norm + 1e-5)

    gain_val = 0.5 * g + 1
    dx = gain_val * gx
    dy = gain_val * gy
    dx[np.abs(dx) > 10] = 0
    dy[np.abs(dy) > 10] = 0

    out = np.zeros((hn, wn))
    cdef int nx, ny, fx, fy, sx, sy
    cdef double wx, wy, w1, w2, w3, w4, val

    for nx in range(10, hn - 10):
        for ny in range(10, wn - 10):
            wx, wy = dx[nx, ny], dy[nx, ny]
            fx, fy = int(wx), int(wy)
            sx, sy = int(np.sign(wx)), int(np.sign(wy))
            w1 = (1 - fabs(wx - fx)) * (1 - fabs(wy - fy))
            w2 = (1 - fabs(wx - fx)) * fabs(wy - fy)
            w3 = fabs(wx - fx) * (1 - fabs(wy - fy))
            w4 = fabs(wx - fx) * fabs(wy - fy)
            val = interp_i[nx, ny]
            out[nx + fx, ny + fy] += w1 * val
            out[nx + fx, ny + fy + sy] += w2 * val
            out[nx + fx + sx, ny + fy] += w3 * val
            out[nx + fx + sx, ny + fy + sy] += w4 * val

    return out[10:-10, 10:-10], interp_i[10:-10, 10:-10], g, r

cpdef tuple dpr_stack(np.ndarray[DTYPE_t, ndim=3] s, double psf, dict opt):
    cdef int f = s.shape[2]
    dpr0, mag0, _, _ = dpr_update_single(s[:, :, 0], psf, opt)
    shp = dpr0.shape
    out = np.zeros((shp[0], shp[1], f))
    mag = np.zeros((shp[0], shp[1], f))
    cdef int i
    for i in range(f):
        dpr, m, _, _ = dpr_update_single(s[:, :, i], psf, opt)
        out[:, :, i] = dpr
        mag[:, :, i] = m
    if opt.get('temporal') == 'mean':
        out = np.mean(out, axis=2)
    elif opt.get('temporal') == 'var':
        out = np.var(out, axis=2)
    return out, mag
cpdef tuple apply_dpr(np.ndarray[DTYPE_t, ndim=3] im, double psf=4, double gain=2, double background=10, temporal='mean'):
    if im.ndim == 2:
        im = im[:, :, np.newaxis]
    opt = dpr_set_parameters(psf, gain, background, temporal)
    return dpr_stack(im, psf, opt)
