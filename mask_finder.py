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
from glob import glob
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_erosion, binary_dilation
from scipy.ndimage import binary_fill_holes
# ---------------------------------------------------------------------------

image_slices_wanted = {"fish1": (147, 288),
                       "fish2": (140, 305),
                       "fish3": (155, 300),
                       "fish4": (160, 270),
                       "fish5": (150, 310)
                      }


def find_threshold(image_slice):
    '''Finds the threshold of a single image slice.'''
    threshold = np.median(image_slice) + 3 * np.std(image_slice)    # Courtesy of prof. Raghu
    return threshold


def load_images_and_find_masks(dirname):
    """ 
    Loads a directory and returns an array of masks for the 
    given channel through filtering operations and thresholding.
    """

    file_lst = glob(dirname)
    sort_nicely(file_lst)

    images_lst = []

    match = re.search('GFP', dirname)
    
    # Initialize the appropriate remove small objects parameter depending 
    # on whether the GFP or RFP directory is passed 
    if match:
        remove_small_objects_parameter = 1000
    else:
        remove_small_objects_parameter = 150

    for unread_image in file_lst:
        image = io.imread(unread_image)
        threshold = find_threshold(image)
        mask = np.where(image<threshold, False, True)
        eroded_and_dilated_mask = binary_erosion(binary_dilation(mask))
        remove_small_objects_mask = remove_small_objects(eroded_and_dilated_mask, remove_small_objects_parameter, in_place=True)
        images_lst.append(binary_fill_holes(remove_small_objects_mask))

    images_array = np.asarray(images_lst)

    return images_array


def main():
    fish_number = input("Which fish are you working with? Type fish1, fish2, fish3, fish4, or fish5.    ")   
    stack_indices = image_slices_wanted.get(fish_number)

    GFP_masks_array = load_images_and_find_masks("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\GFP\*.tif")[stack_indices[0]:stack_indices[1]]  
    RFP_masks_array = load_images_and_find_masks("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\RFP\*.tif")[stack_indices[0]:stack_indices[1]]  

    intersection_array = remove_small_objects(np.logical_and(GFP_masks_array, RFP_masks_array), 200, in_place=True)

    # Free unnecessary memory 
    del GFP_masks_array
    del RFP_masks_array
    
    np.savez_compressed("intersection_finder_output.npz", intersection_array)

    


if __name__ == '__main__':
    main()


