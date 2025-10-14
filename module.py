from matplotlib.path import Path 

import numpy  as np
import pandas as pd
import h5py
from pathlib import Path

from astropy    import units as u
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
# matplotlib.use('Agg')

from scipy.interpolate import RegularGridInterpolator
from scipy.signal      import argrelextrema

from common import hallmark as hm
from common import mockservation as mk
from common import io_raptor as io
from common import dalt
from common import viz

import plotscripts
from plotscripts import subtract, image2d, loadfigure, getimagedata

import rapplot




# ====================================================

def import_ab(a, i, cond):
    file = f'output/shadow_a{a:.2f}_i{i:g}.h5' # change this to your local folder
    with h5py.File(file) as h:
      alpha = h['a'][:]
      beta = h['b'][:]

    if cond:
      index_apos = np.where(alpha > 0)[0]
      aright = index_apos[beta[index_apos].argmin()]

      for bb in np.linspace(-10e-3, 10e-3, 10):
        alpha = np.append(alpha, alpha[aright])
        beta = np.append(beta, bb)

    return (alpha, beta)
# ====================================================



def plotregion(imgs, ax):
 
    intensity = np.sum(imgs, axis=0)
    dominant_index = np.argmax(imgs, axis=0)
    dominant_index[intensity <=1e-16 ] = -1  # Mark zero-intensity regions

  
    cmap = plt.get_cmap('tab10')
    colors = [cmap(9)] + [cmap(i) for i in range(3)]  # Background + n0, n1, n2
    color_map = np.array(colors)

    display_index = dominant_index + 1  # Shift -1 to 0, 0→1, etc.
    ax.imshow(display_index, origin='lower', cmap=plt.matplotlib.colors.ListedColormap(color_map),
              extent=[-20, 20, -20, 20])

    labels = ['Background', 'n0', 'n1', 'n2']
    handles = [mpatches.Patch(color=color_map[i], label=labels[i]) for i in range(4)]

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)

    return handles


def plot_va(mov, ax, n): 
    vis = mk.mockserve(mov, N=6000)

    U, V = vis.uvd
    u = np.linspace(0, U/2, num=vis.shape[-1])
    v = np.linspace(-V/2, V/2, num=vis.shape[-2], endpoint=False)
    t = vis.meta.time.value

    amp = RegularGridInterpolator((t, v, u[::-1]), abs(vis[..., ::-1]))
    phi = RegularGridInterpolator((t, v, u[::-1]), np.angle(vis[..., ::-1]))

    bmin = 6e9
    bmax = 20e9
    uvd = np.linspace(0, bmax, 1000)

    i = 0
    phi_angle = np.pi * i / 180
    u = uvd * np.cos(phi_angle)
    v = uvd * np.sin(phi_angle)

    mask = u <= 0
    p = np.array([np.repeat(t[0], np.sum(mask)), v[mask], u[mask]]).T
    m = np.array([np.repeat(t[0], np.sum(~mask)), -v[~mask], -u[~mask]]).T

    s = np.zeros(len(uvd))
    s[mask] = amp(p)
    s[~mask] = amp(m)

    uvd_G = uvd / 1e9 
    s_Jy = s * 1e-26 

    if n == 100:
        line, = ax.semilogy(uvd_G, s_Jy, '-', linewidth=0.5, label='Total')
    else:
        line, = ax.semilogy(uvd_G, s_Jy, '-', linewidth=0.5, label=f'n={n}')

    return [line]

def connectcurve(alpha, beta):
    
    return 