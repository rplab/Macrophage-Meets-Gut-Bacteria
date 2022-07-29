# !/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Estelle Trieu 
# Created Date: 4/26/2022
# version ='1.0'
# ---------------------------------------------------------------------------
""" 
This module identifies intersection events (macrophage engulfing gut bacteria)
between GFP and RFP channels and loads the results to a numpy compressed file.
The intersection mask is found by finding the product of the GFP and RFP masks,
which are created through filtering operations and the thresholding formula
threshold = median + 3 * standard deviation. Runtime for 1 fish / 1 pos /
1 timepoint is 10 minutes. 
""" 
# ---------------------------------------------------------------------------
import numpy as np
import re
import itertools
from glob import glob
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_dilation
from scipy.ndimage import binary_fill_holes
# ---------------------------------------------------------------------------

# The first and last 100 or so images definitely do not have 
# intersection events, so we exclude them from analysis  
image_slices_wanted = {"Fish1": (130, 395),
                       "Fish2": (145, 420),
                       "Fish3": (140, 355),
                       "Fish4": (185, 450),
                       "Fish5": (340, 475)}

timepoints_wanted =   {"Fish1": 5,
                       "Fish2": 13,
                       "Fish3": 13,
                       "Fish4": 4,
                       "Fish5": 5}


def find_threshold(image_slice):
    '''Finds the threshold of a single image slice.'''
    threshold = np.median(image_slice) + 3 * np.std(image_slice)    # Courtesy of prof. Raghu
    return threshold


def load_images_and_find_masks(dirname, stack_indices):
    """ 
    Loads a directory and returns an array of masks for the 
    given channel through filtering operations and thresholding.
    """

    file_lst = glob(dirname)
    sort_nicely(file_lst)

    masks_lst = []

    match = re.search('GFP', dirname)
    
    # Initialize the appropriate remove small objects parameter depending 
    # on whether the GFP or RFP directory is passed 
    if match:
        remove_small_objects_parameter = 500
    else:
        remove_small_objects_parameter = 600

    for unread_image in file_lst:
        image = io.imread(unread_image)
        mask = remove_small_objects(
        binary_dilation(np.where(image<find_threshold(image), False, True)), remove_small_objects_parameter, in_place=True)
        masks_lst.append(binary_fill_holes(mask))

    images_array = (np.asarray(masks_lst))[stack_indices[0]:stack_indices[1]]  
    
    return images_array


def main():
    fish_dir = glob("L:\Julia_10March\*")   # the parent directory that holds all the nested folders for the 5 fish
    sort_nicely(fish_dir)

    # Loop through each of the 5 fish
    for fish in fish_dir:
        if re.search('Fish[0-9]', fish):
            timepoint_dir = glob(f"{fish}\*") 
            sort_nicely(timepoint_dir)
            fish_number = re.search('Fish[0-9]', fish).group()     
            stack_indices = image_slices_wanted.get(fish_number)
            n = timepoints_wanted[fish_number]

            # Loop through the timepoints for each fish
            for timepoint in itertools.islice(timepoint_dir, n):
                timepoint_number = re.search('Timepoint[0-9]*', timepoint).group()
                pos_dir = glob(f"{timepoint}\*")
                sort_nicely(pos_dir)
                
                # Loop through the 4 positions for each fish
                for pos in pos_dir:
                    pos_number = re.search('Pos[0-9]', pos).group()

                    # Load images by passing the full path to the appropriate function 
                    GFP_masks_array = load_images_and_find_masks(f"{pos}\zStack\GFP\*.tif", stack_indices)
                    RFP_masks_array = load_images_and_find_masks(f"{pos}\zStack\RFP\*.tif", stack_indices)
        
                    intersection_array = remove_small_objects(np.logical_and(GFP_masks_array, RFP_masks_array), 200, in_place=True)

                    # Free unnecessary memory 
                    del GFP_masks_array
                    del RFP_masks_array
                    
                    np.savez_compressed(
                    f"L:\Julia_10March\intersection_mask_arrays\{fish_number}-{timepoint_number}-{pos_number}.npz", intersection_array)


  


if __name__ == '__main__':
    main()


    
    
    
    
    
    
    

    


