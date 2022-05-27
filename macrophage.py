import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_erosion, binary_opening
from scipy.ndimage import binary_fill_holes
from skimage.measure import label, regionprops

## Improvements: (1) closing holes in images - dialation? (2) np vmin & vmax ##

def load_images(dirname):
    file_lst = glob(dirname)
    sort_nicely(file_lst)
    image_array = np.array([io.imread(i) for i in file_lst])
    return image_array
    

def find_threshold(array):
    median = np.median(array)
    std = np.std(array)
    threshold = median + 3 * std    # Courtesy of prof. Raghu
    return threshold


def find_masks(array):
    images_lst = []

    for image_array in array:
        threshold = find_threshold(image_array)
        mask = np.where(image_array<threshold, 0, 1)
        bool_mask = np.array(mask, bool)
        small_objects_removed_mask = np.array(remove_small_objects(bool_mask, 2200, in_place=True), int) 
        binary_opening(small_objects_removed_mask)       # Remove noise
        binary_fill_holes(small_objects_removed_mask)    # Close any holes from image opening
        cleaned_mask = binary_erosion(small_objects_removed_mask)
        images_lst.append(cleaned_mask)

    images_array = np.asarray(images_lst)

    return images_array

def product_of_masks(array1, array2):
    intersection = np.logical_and(array1, array2)
    return intersection

def get_regions(array):
    labeled_mask = label(array)
    regions = regionprops(labeled_mask)
    return regions

"""
TO DO:
def show_subset_image(array):
    return
"""


def main():
    GFP_image_array = load_images("C:/Pos1_/Pos1/zStack/GFP/Default/*.*")
    RFP_image_array = load_images("C:/Pos1_/Pos1/zStack/RFP/Default/*.*")

    GFP_masks_array = find_masks(GFP_image_array)
    RFP_masks_array = find_masks(RFP_image_array)

    mask_intersection = product_of_masks(GFP_masks_array, RFP_masks_array)
    regions = get_regions(mask_intersection)



if __name__ == '__main__':
    main()

