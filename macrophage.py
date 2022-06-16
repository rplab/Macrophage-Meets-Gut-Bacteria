import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_erosion, binary_opening, binary_dilation
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
        cleaned_mask = binary_dilation(binary_erosion(small_objects_removed_mask))      # Dilation and erosion of image
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

def show_subset_image(image_array, masks_array, regions_array):
    for idx, image in enumerate(image_array):
        for region in regions_array:
            coord = region.coords

                plt.figure()
        
                plt.imshow(image_array[idx][0:(coord[0]+300), (coord[1]+100):2000], cmap='gray')
                plt.imshow(masks_array[idx][0:(coord[0]+300), (coord[1]+100):2000], alpha=0.2, cmap='gray_r')



def main():
    GFP_image_array = load_images("C:/Pos1_/Pos1/zStack/GFP/Default/*.*")
    # RFP_image_array = load_images("C:/Pos1_/Pos1/zStack/RFP/Default/*.*")

    GFP_masks_array = find_masks(GFP_image_array)
    # RFP_masks_array = find_masks(RFP_image_array)

    # plt.figure()
    # plt.imshow(GFP_image_array[0], cmap='gray')

    # plt.figure()
    # plt.imshow(GFP_image_array[0], cmap='gray')
    # plt.imshow(GFP_masks_array[0], alpha=0.2, cmap='gray_r')


    # mask_intersection = product_of_masks(GFP_masks_array, RFP_masks_array)
    # regions = get_regions(mask_intersection)
    # show_subset_image(GFP_image_array, regions)





if __name__ == '__main__':
    main()

