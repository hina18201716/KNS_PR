# %load_ext autoreload
# %autoreload 2

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib
# matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.image as mpimg
import h5py
import rapplot
from rapplot import read_data_id, read_data, plot_data_stokes


#Computing relevant constants
M=5e6 * rapplot.MSUN
d=8 * rapplot.KPC

rg = (rapplot.G*M/rapplot.SPEED_OF_LIGHT**2.)

mas = (rg/d)* rapplot.MAS_IN_DEG

Tunit =rg/rapplot.SPEED_OF_LIGHT

halfrange=20 #in rg

def read_avedata_id(folder,ind):
    file_name = folder+'/aveimg_%d.h5'%ind
#     print("Reading keys from: ", file_name)
    images = h5py.File(file_name,'r')
    keys = [key for key in images.keys()]
#     print(keys)
    images.close()
    return keys


def read_avedata(folder,ind,data_id):

    file_name = folder+'/aveimg_%d.h5'%ind

    print("Reading in: ", file_name)

    images = h5py.File(file_name,'r')

    min = [-100.,-100.,-100.,-100.]
    max = [100.,100.,100,100.]
    print(len(data_id))
    for j in range(0,len(data_id)-4):
        for i in range(0,len(images[data_id[j]])):
            current=np.max(images[data_id[j]][i])
            max[j]=np.maximum(max[j],np.max(images[data_id[j]][i]))
            min[j]=np.minimum(min[j],np.min(images[data_id[j]][i]))

    return min,max,images

def average_snapshots_to_h5(path, start_ind, end_ind, nzero=False):
    '''
    Function to create hdf5 file of snapshot average. 
    input: 
        path : path to the directry to fold datasets
        start_ind : snapshot index to start averaging 
        end_ind : snapshot index to finish averaging 
    '''
#     number of snapshot to average
    n = end_ind - start_ind
    
# find path to set of snapshot
    if nzero: 
        folder = f"{path}/nzero"
    else: 
        folder = f"{path}/nall"
    print(f"read from {folder}")
    
 # Get initial structure 
    data_id = read_data_id(folder, start_ind)
    minval, maxval, images = rapplot.read_data(folder, start_ind, data_id)
    
# Create a float64 dictionary to hold the sum
    summed = {key: np.zeros_like(images[key][:], dtype=np.float64) for key in images.keys()}

    for ind in range(start_ind, end_ind + 1):
       
        data_id = read_data_id(folder, ind)
        _, _, images = rapplot.read_data(folder, ind, data_id)

        for key in summed:
            summed[key] += images[key][:].astype(np.float64)

    for key in summed:
        summed[key] /= n

#    create a new hdf5 file for averaged data 
    output_file = folder+'/aveimg_%d.h5'%n
    if os.path.exists(output_file):
        os.remove(output_file)  # Overwrite if already exists

    with h5py.File(output_file, 'w') as f:
        for key in summed:
            f.create_dataset(key, data=summed[key])
            
            
def getimagedata(img_path, ind, stokes_ind=0, resize=True): 
    
    data_id = rapplot.read_data_id(img_path, ind)
    min, max, image = rapplot.read_data(img_path, ind, data_id)
    if resize: 
        image = image2d(image, stokes_ind, data_id)
        
    if isinstance(image, h5py.File):
        print("file converted")
        keys = list(image.keys())
        image = image[keys[stokes_ind]][()] 
    
    return data_id, min, max, image
            
def subtract(pathA, pathB, start_ind=100, end_ind=500, ave=True): 
    '''Average snapshots and subtract to get high order photon rings. 
    input: 
        path: path to the data
        inc : observation angle 
        a : spin parameter
    ---------------
    output : 
        data_id : keys of hdf5
        min : array of minimum values for each strokes 
        max : array of maximum values for each strokes 
        hpr : image data (2d numpy array)
    '''
    
    # path = f"output/a{a}/i{inc}"
    print(f"read from {pathA} and {pathB}")

    if ave: 
        # make sure images to download is already averaged 
        average_snapshots_to_h5(pathA, start_ind, end_ind, False)
        average_snapshots_to_h5(pathB, start_ind, end_ind, True)

        # Get initial structure 
        data_id_A  = read_avedata_id(pathA, start_ind)
        data_id_B  = read_avedata_id(pathB, start_ind)

        min_A, max_A,  img_A = read_avedata(pathA, start_ind, data_id_A)    
        min_B, max_B,  img_B = read_avedata(pathB, start_ind, data_id_B)

    else: 
        # Get initial structure 
        data_id_A  = rapplot.read_data_id(pathA, start_ind)
        data_id_B  = rapplot.read_data_id(pathB, start_ind)

        min_A, max_A,  img_A = rapplot.read_data(pathA, start_ind, data_id_A)    
        min_B, max_B,  img_B = rapplot.read_data(pathB, start_ind, data_id_B)
     
    # Create a float64 dictionary to hold the sum
    sub_file = {key: np.zeros_like(img_A[key][:], dtype=np.float64) for key in img_A.keys()}
    for key in sub_file:
        sub_file[key] = img_A[key][:].astype(np.float64) - img_B[key][:].astype(np.float64)
    
    n = start_ind+1
#    create a new hdf5 file 
    output_file = pathA+'/img_data_%d.h5'%n
    if os.path.exists(output_file):
        os.remove(output_file) 

    with h5py.File(output_file, 'w') as f:
        for key in sub_file:
            f.create_dataset(key, data=sub_file[key])
            
# read in and return 
    data_id_A  = rapplot.read_data_id(pathA, n)
    min_A, max_A,  sub = rapplot.read_data(pathA, n, data_id_A)    
        
    sub_array = image2d(sub, 0, data_id_A)
    sub_array[sub_array<0] = 0
   
    #TODO: check if 0-2 is same as ones from zero
    return data_id_A, min_A, max_A, sub_array
  
def image2d(image, stokes_ind, data_id):
    """Create 2D array of one of the Stokes parameters for plotting."""

    n_box = len(image[data_id[stokes_ind]])              #depends on camera pixles you chose for GRRT   
    n_pixel_per_box = len(image[data_id[stokes_ind]][0]) #100
    pixels = int(np.sqrt(n_pixel_per_box))  # pixels per block side 10x10 

    n_blocks_side = int(round(np.sqrt(n_box)))
    
    # Total image dimensions
    width = n_blocks_side * pixels
    height = (n_box // n_blocks_side) * pixels
    
    image_array = np.zeros((height, width), dtype=float)

    for i in range(n_box):
        block_row = i // n_blocks_side
        block_col = i % n_blocks_side
        block_data = np.array(image[data_id[stokes_ind]][i])
        array = np.reshape(block_data, (pixels, pixels))
        image_array[
            block_row*pixels:(block_row+1)*pixels,
            block_col*pixels:(block_col+1)*pixels
        ] = array
    image_array[image_array<0] = 0

    return image_array.T  
                               
def loadfigure(image_array, min, max, fig, ax, halfrange=20, mas=1, label="Stokes", cmap="afmhot"): 
    '''This function create figure of one image. 
    '''
    extent = [-halfrange * mas, halfrange * mas, -halfrange * mas, halfrange * mas]
    figure = ax.imshow((image_array/np.max(image_array))**0.5, vmin=0.0, vmax=1.0, cmap=cmap, origin='lower', extent=extent)
  
    return figure 


def writehdf5(img_path, img_new, img_temeplate, snap):  
    newfile = {key: np.zeros_like(img_template[key][:], dtype=np.float64) for key in img_template.keys()}
    for key in newfile:
        newfile[key[0]] = img_new.astype(np.float64) 
    
#    create a new hdf5 file for averaged data 
    output_file = img_path+f'/img_data_10{snap}.h5'
    if os.path.exists(output_file):
        os.remove(output_file)  # Overwrite if already exists

    with h5py.File(output_file, 'w') as f:
        for key in sub_file:
            f.create_dataset(key, data=sub_file[key])
    return output_file