# !/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Estelle Trieu 
# Created Date: 4/26/2022
# version ='1.0'
# ---------------------------------------------------------------------------
""" 
This module loads a numpy compressed file from intersection_finder.py and  
saves image slices with intersection events and their respective maximum
intensity projection applied to a folder. Runtime for 1 fish / 1 pos /
1 timepoint is 3 minutes. 
""" 
# ---------------------------------------------------------------------------
import numpy as np
from numpy import *
from glob import glob
import matplotlib
import matplotlib.pyplot as plt
import imageio as io
from image_operations import sort_nicely
from skimage.measure import label, regionprops
# ---------------------------------------------------------------------------

image_slices_wanted = {"fish1": (147, 288),
                       "fish2": (140, 305),
                       "fish3": (155, 300),
                       "fish4": (160, 270),
                       "fish5": (150, 310)
                      }


fish_number = input("Which fish are you working with? Type fish1, fish2, fish3, fish4, or fish5.    ")   
stack_indices = image_slices_wanted.get(fish_number)


def load_intersection_array(npz_file):
    '''Loads a intersection array from a numpy compressed file.'''
    intersection_array = (load(npz_file))['arr_0']     # the array is stored at the 0th index
    return intersection_array


def load_images(dirname):
    '''Loads and reads the images of a directory into an array.'''
    file_lst = glob(dirname)
    sort_nicely(file_lst)
    image_array = (np.array([io.imread(i) for i in file_lst]))[stack_indices[0]:stack_indices[1]]
    return image_array


def get_bounding_box(array):
    '''Returns a list of bounding boxes of a given array.'''
    bboxes = []

    mask_props = regionprops(label(array))

    # Find the bounding box of each intersection region 
    for prop in mask_props:
        bbox = prop.bbox
        bboxes.append(bbox)    

    return bboxes
    

def show_subset_image(GFP_image_array, RFP_image_array, intersection_masks_array, intersection_bboxes):
    """ 
    Displays the maximum intensity projection of images slices with 
    intersection events using the bounding boxes of associated
    intesection regions for each image slice.
    """

    # Find the max intensity projection along the z axis of a collection of image slices 
    for bbox in intersection_bboxes:                                                                     # bbox is of the form (z_min, y_min, x_min, z_max, y_max, x_max)                                                                                                                 
        GFP_max_proj_array = np.amax(GFP_image_array[bbox[0]:bbox[3]+1], axis=0)         # bbox[3]+1 accounts for the fact that slicing starts at 0 and ends at N-1                
        RFP_max_proj_array = np.amax(RFP_image_array[bbox[0]:bbox[3]+1], axis=0)
        intersection_masks_max_proj_array = np.amax(intersection_masks_array[bbox[0]:bbox[3]+1], axis=0)    # axis=0 gives the projection along the z axis

        fig, axs = plt.subplots(2, 2)

        # axs[0,0] and axs[0,1] display the entire image with a rectangular box capturiung the intersection
        axs[0, 0].imshow(GFP_max_proj_array, cmap='gray')  
        axs[0, 0].imshow(intersection_masks_max_proj_array, alpha=0.2, cmap='gray_r')
        rect = matplotlib.patches.Rectangle((bbox[2], bbox[1]), 2 * (bbox[5] - bbox[2]), 2 * (bbox[4] - bbox[1]), linewidth=1, edgecolor='r', facecolor='none')
        axs[0, 0].add_patch(rect)
        axs[0, 0].set_title(f"MIP of GFP imgs {bbox[0]+ stack_indices[0]}-{bbox[3]+1+stack_indices[0]}")
        axs[0, 0].xaxis.set_ticklabels([])              # Delete tick labels 
        axs[0, 0].yaxis.set_ticklabels([])
        axs[0, 0].tick_params(bottom=False)      # Delete tick marks on x axis
        axs[0, 0].tick_params(left=False)        # Delete tick marks on y axis

        axs[0, 1].imshow(RFP_max_proj_array, cmap='gray') 
        axs[0, 1].imshow(intersection_masks_max_proj_array, alpha=0.2, cmap='gray_r') 
        rect = matplotlib.patches.Rectangle((bbox[2], bbox[1]), 2 * (bbox[5] - bbox[2]), 2 * (bbox[4] - bbox[1]), linewidth=1, edgecolor='r', facecolor='none')
        axs[0, 1].add_patch(rect)
        axs[0, 1].set_title(f"MIP of RFP imgs {bbox[0]+ stack_indices[0]}-{bbox[3]+1+stack_indices[0]}")
        axs[0, 1].xaxis.set_ticklabels([])
        axs[0, 1].yaxis.set_ticklabels([])
        axs[0, 1].tick_params(bottom=False)      
        axs[0, 1].tick_params(left=False)  

        axs[1, 0].imshow((GFP_image_array[bbox[0]])[bbox[1]:bbox[4], bbox[2]:bbox[5]], cmap='gray')
        axs[1, 0].imshow((intersection_masks_array[bbox[0]])[bbox[1]:bbox[4], bbox[2]:bbox[5]], alpha=0.2, cmap='gray_r')
        axs[1, 0].xaxis.set_ticklabels([])
        axs[1, 0].yaxis.set_ticklabels([])
        axs[1, 0].tick_params(bottom=False)      
        axs[1, 0].tick_params(left=False)  

        axs[1, 1].imshow((RFP_image_array[bbox[0]])[bbox[1]:bbox[4], bbox[2]:bbox[5]], cmap='gray')
        axs[1, 1].imshow((intersection_masks_array[bbox[0]])[bbox[1]:bbox[4], bbox[2]:bbox[5]], alpha=0.2, cmap='gray_r')
        axs[1, 1].xaxis.set_ticklabels([])
        axs[1, 1].yaxis.set_ticklabels([])
        axs[1, 1].tick_params(bottom=False)      
        axs[1, 1].tick_params(left=False)  
        
        plt.savefig(f"L:\Estelle_fish2_pos1_time1_images\image_{bbox[0]+stack_indices[0]}-{bbox[3]+1+stack_indices[0]}")          # Save images to a folder labeled with the image slices used in the projection
        plt.close(fig)


def main():
    intersection_masks_array = load_intersection_array("intersection_finder_output.npz")
   
    GFP_image_array = load_images("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\GFP\*.tif")
    RFP_image_array = load_images("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\RFP\*.tif")

    intersection_bboxes = get_bounding_box(intersection_masks_array)

    show_subset_image(GFP_image_array, RFP_image_array, intersection_masks_array, intersection_bboxes)




if __name__ == '__main__':
    main()
