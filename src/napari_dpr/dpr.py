import os, sys, time, numpy as np, scipy.ndimage as ndi
from scipy.interpolate import RectBivariateSpline
import tifffile as tiff
from PIL import Image
import matplotlib.pyplot as plt

## original DPR as shown by https://github.com/biomicroscopy/DPR-Resolution_enhancement_with_deblurring_by_pixel_reassignment

def dpr_set_parameters(psf, **k): return {'gain': k.get('gain',1), 'background': k.get('background',int(np.ceil(17*psf))), 'temporal': k.get('temporal',None)}

def dpr_update_single(i, psf, opt):
    g, r = opt['gain'], int(np.ceil(opt['background']))
    psf /= 1.6651
    h, w = i.shape
    x0, y0 = np.linspace(-.5,.5,w), np.linspace(-.5,.5,h)
    x, y = np.linspace(-.5,.5,round(5*w/psf)), np.linspace(-.5,.5,round(5*h/psf))
    sx, sy = np.array([[1,0,-1],[2,0,-2],[1,0,-1]]), np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
    i = i - i.min()
    localmin = np.zeros_like(i)
    i_localmin = np.zeros_like(i)
    for u in range(h):
        for v in range(w):
            sub = i[max(0,u-r):min(h,u+r+1), max(0,v-r):min(w,v+r+1)]
            localmin[u,v] = sub.min()
            i_localmin[u,v] = i[u,v] - localmin[u,v]
    m = RectBivariateSpline(y0,x0,i_localmin)(y,x)
    m[m<0] = 0
    m = np.pad(m,10)
    mag = RectBivariateSpline(y0,x0,i)(y,x)
    mag[mag<0] = 0
    mag = np.pad(mag,10)
    hn, wn = mag.shape
    norm = m / (ndi.gaussian_filter(m,10)+1e-5)
    gx = ndi.convolve(norm, sy, mode='reflect') / (norm + 1e-5)
    gy = ndi.convolve(norm, sx, mode='reflect') / (norm + 1e-5)
    d = 0.5*g+1
    dx, dy = d*gx, d*gy
    dx[np.abs(dx)>10] = 0
    dy[np.abs(dy)>10] = 0
    out = np.zeros((hn, wn))
    for nx in range(10, hn-10):
        for ny in range(10, wn-10):
            wx, wy = dx[nx,ny], dy[nx,ny]
            fx, fy = int(wx), int(wy)
            sx, sy = int(np.sign(wx)), int(np.sign(wy))
            w1 = (1-abs(wx-fx))*(1-abs(wy-fy))
            w2 = (1-abs(wx-fx))*abs(wy-fy)
            w3 = abs(wx-fx)*(1-abs(wy-fy))
            w4 = abs(wx-fx)*abs(wy-fy)
            c1 = [fx, fy]
            c2 = [fx, fy+sy]
            c3 = [fx+sx, fy]
            c4 = [fx+sx, fy+sy]
            val = mag[nx,ny]
            out[nx+c1[0], ny+c1[1]] += w1*val
            out[nx+c2[0], ny+c2[1]] += w2*val
            out[nx+c3[0], ny+c3[1]] += w3*val
            out[nx+c4[0], ny+c4[1]] += w4*val
    return out[10:-10,10:-10], mag[10:-10,10:-10], g, r

def dpr_stack(s, psf, o):
    f = s.shape[2]
    shp = dpr_update_single(s[:,:,0],psf,o)[1].shape
    out = np.zeros((*shp,f)); mag = np.zeros((*shp,f))
    for i in range(f):
        sys.stdout.write(f"\rProcessing {i+1}/{f}"); sys.stdout.flush()
        o1,o2,_,_ = dpr_update_single(s[:,:,i],psf,o)
        out[:,:,i], mag[:,:,i] = o1, o2
    t = o.get('temporal','')
    if t == 'mean': out = np.mean(out,axis=2)
    elif t == 'var': out = np.var(out,axis=2)
    return out, mag

def load_image_stack(p,n,t):
    path = os.path.join(p,f'{n}.{t}')
    if t.lower() == 'tif':
        d = tiff.imread(path)
        return np.transpose(d,(1,2,0)) if d.ndim==3 else d
    return np.array(Image.open(path))

def save_image(im, p, n, t):
    os.makedirs(p, exist_ok=True)
    f = os.path.join(p, f'{n}.{t}')
    if t.lower()=='tif': tiff.imwrite(f, im)
    else:
        if im.dtype != np.uint8:
            im = ((im-im.min())/(im.max()-im.min())*255).astype(np.uint8)
        Image.fromarray(im).save(f)

def process_image(p,n,t,psf,o):
    s = load_image_stack(p,n,t)
    out, mag = dpr_stack(s, psf, o)
    save_image(out, os.path.join(p,'DPR_results'), f'{n}_result', t)
    return s, out, mag

def display_images(i,m,o):
    plt.figure(figsize=(12,4))
    plt.subplot(1,3,1); plt.imshow(i[...,0] if i.ndim==3 else i, cmap='gray'); plt.title('Initial')
    plt.subplot(1,3,2); plt.imshow(np.mean(m,axis=2) if m.ndim==3 else m, cmap='gray'); plt.title('Magnified')
    plt.subplot(1,3,3); plt.imshow(o, cmap='gray'); plt.title('DPR')
    plt.tight_layout(); plt.show()

def main():
    p = r'test_data'
    f = input("File name [test_image.tif]: ") or "test_image.tif"
    n,t = f.rsplit('.',1)
    mode = input("Use default params? y/n/e [y]: ").lower() or 'y'
    if mode == 'e':
        print("PSF: blur radius\nGain: enhancement\nBackground: subtraction\nTemporal: mean or var")
        mode = input("Use default now? y/n [y]: ").lower() or 'y'
    if mode == 'y': psf,g,bg,tmp = 4,2,10,'mean'
    else:
        psf = float(input("PSF [4]: ") or 4)
        g = float(input("Gain [2]: ") or 2)
        bg = float(input("Background [10]: ") or 10)
        tmp = input("Temporal [mean]: ") or 'mean'
    o = dpr_set_parameters(psf, gain=g, background=bg, temporal=tmp)
    start = time.time()
    res = process_image(p,n,t,psf,o)
    if res:
        img,dpr,mag = res
        print(f"\nTime: {time.time()-start:.2f}s")
        display_images(img,mag,dpr)
    else: print("Failed.")

def apply_dpr(im, psf=4, gain=2, background=10, temporal='mean'):
    if im.ndim == 2: im = im[:,:,np.newaxis]
    o = dpr_set_parameters(psf, gain=gain, background=background, temporal=temporal)
    return dpr_stack(im, psf, o)

if __name__ == '__main__': main()
