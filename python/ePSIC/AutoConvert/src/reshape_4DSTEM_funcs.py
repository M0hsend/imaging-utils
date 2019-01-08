import hyperspy.api as hs
import numpy as np
from math import floor
from pathlib import Path
import pylab as plt
import matplotlib.pyplot as plt
import os
import time
import sys
from scipy.signal import find_peaks


def reshape_4DSTEM_FrameSize(data, scan_x, scan_y):
    """
    Reshapes the lazy-imported stack of dimensions: (xxxxxx|256, 256) to the correct scan pattern shape:
    It gets the scan pattern dimensions from the user as input and reshapes from the end of the stack
    to start to avoid having the fly-back falling in the centre.
    
    NB: The fly-back can be included in the reshaped frame!
    
    Inputs:
        data: hyperspy lazily imported mib file with diensions of: framenumbers|256, 256
        scan_x: number of lines
        scan_y: number of probe positions in every line
    Outputs:
        data_reshaped : reshaped data (scan_x, scan_y | 256,256)
    """
    frames_total = scan_x * scan_y
    
    if frames_total <= data.axes_manager[0].size:
        skip = data.axes_manager[0].size - frames_total
        print(skip)
        data_skip = data.inav[skip:]
        data_skip.data = data_skip.data.reshape(scan_x, scan_y, 256, 256)
        data_skip.axes_manager._axes.insert(0, data_skip.axes_manager[0].copy())
        data_skip.get_dimensions_from_data() #reshaped
        
    else:
        print('================================================================')
        print('Total number of frames is less then the scan_x*scan_y provided.')
        print('Retuning the stack without reshaping.')
        print('================================================================')

        data_skip = data
    
    return data_skip

def reshape_4DSTEM_FlyBack(data, scan_x, plot_sum = False):
    """
    Reshapes the lazy-imported stack of dimensions: (xxxxxx|256, 256) to the correct scan pattern 
    shape: (x, y | 256,256).
    It utilises the over-exposed fly-back frame to identify the start of the lines in the first 10
    lines of frames,checks line length consistancy and finds the number of frames to skip at the
    beginning (this number is printed out as string output).
    
    Parameters
    ----------
    data : hyperspy lazily imported mib file with diensions of: framenumbers|256, 256
    plot_Sum: (default: Flase) Set to True to get the intensity profile of the first 10 lines
                - to check for peak finding correctness
       
    Returns
    -------
    data_reshaped : reshaped data (x, y | 256,256)
    optional: plots the sum intensity vs frames
    """
    data_crop = data.inav[0:np.int(10* np.sqrt(data.axes_manager[0].size))] #crop the first ~10 lines
    data_crop_t = data_crop.T
    data_crop_t_sum = data_crop_t.sum()
    intensity_array = data_crop_t_sum.data #summing over patterns
    intensity_array = intensity_array.compute() #out of lazy
    #Checking for local maxima to be more than _factor_ times the neighbouring elements
    #This factor is currently not robust to all datasets!
    #factor = np.int(max(intensity_array) / np.mean(intensity_array))
    #print(factor)
    #local_max = (np.r_[True, intensity_array[1:] > factor* intensity_array[:-1]] 
    #        & np.r_[intensity_array[:-1] > factor* intensity_array[1:], True])
    peaks = find_peaks(intensity_array, distance= scan_x)
    if plot_sum == True:
        import matplotlib.pyplot as plt
        
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(121)
        ax2 = fig1.add_subplot(122)
        
        ax1.plot(intensity_array, 'k')
        ax2.plot(peaks[0],np.ones(len(peaks[0])),'*')
        
        ax1.set_title('sum intensity of first ~10 lines of frame')
        ax2.set_title('peaks detected')
    
    #peaks = np.ravel(np.where(local_max))
    lines = np.ediff1d(peaks[0]) #Diff between consecutive elements of the array
    line_len = lines[lines.size-1] # Assuming the last element to be the line length
    check = np.ravel(np.where(lines == line_len)) #Checking line lengths
    
    line_confirm = [np.ediff1d(check) == 1]
    if ~np.all(line_confirm): #In case there is a False in there take the index of the last False
        
        start_ind = np.where(line_confirm[0] == False)[-1][-1] + 2
        skip_ind = peaks[0][start_ind]
        
    else: #In case they are all True take the index of the first True
        skip_ind = peaks[0][check[0]] #number of frames to skip at the beginning
       
      
    n_lines = floor((data.data.shape[0] - skip_ind) / line_len) #Number of lines
    data_skip = data.inav[skip_ind:skip_ind + (n_lines * line_len)] #with the skipped frames removed
    
    data_skip.data = data_skip.data.reshape(n_lines, line_len, 256, 256)
    data_skip.axes_manager._axes.insert(0, data_skip.axes_manager[0].copy())
    data_skip.get_dimensions_from_data() #reshaped
    
    print('Number of frames skipped at the beginning: ', skip_ind)
    data_skip = data_skip.inav[1:]
    return data_skip


