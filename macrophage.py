import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_erosion, binary_dilation
from scipy.ndimage import binary_fill_holes
from skimage.measure import label, regionprops
import time

# --- FUTURE IMPROVEMENTS (low importance) ---
# Use regionprops to find all centroid of all objects 
# Look at GFP and RFP overlaid with mask separately with subplot
# Save intersection: the whole 3D mask as a numpy compressed file
# In a different python file, have a function that takes the numpy compressed file and finds the regions associated with the intersection, and displays it

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

    for image_slice in array:
        threshold = find_threshold(image_slice)
        mask = np.where(image_slice<threshold, False, True)
        eroded_and_dilated_mask = binary_erosion(binary_dilation(mask))
        remove_small_objects_mask = remove_small_objects(eroded_and_dilated_mask, 100, in_place=True)
        binary_fill_holes(remove_small_objects_mask)
        images_lst.append(remove_small_objects_mask)

    images_array = np.asarray(images_lst)
    return images_array


def product_of_masks(array1, array2):
    intersection = np.logical_and(array1, array2)
    return intersection


def get_bounding_box(array):
    bboxes = []

    for mask_idx, mask in enumerate(array):  
        if len(mask) != 0:      # if there's an engulfing event 
            single_mask_props = regionprops(label(mask))

            # Find the bounding box of each intersection region 
            for prop in single_mask_props:
                bbox = prop.bbox
                bboxes.append([mask_idx, bbox])     # Save the index of the image/mask with the corresponding bounding box

    return bboxes

    
def show_subset_image(GFP_image_array, RFP_image_array, intersection_masks_array, bboxes):
    for lst in bboxes:
        image_idx = lst[0]
        bbox = lst[1]
    
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.imshow((GFP_image_array[image_idx])[bbox[0]:bbox[2], bbox[1]:bbox[3]], cmap='gray')

        plt.subplot(2, 1, 2)
        plt.imshow((RFP_image_array[image_idx])[bbox[0]:bbox[2], bbox[1]:bbox[3]], cmap='gray')

        plt.figure()
        plt.subplot(2, 1, 1)
        plt.imshow((GFP_image_array[image_idx]), cmap='gray')                     
        plt.imshow((intersection_masks_array[image_idx])[bbox[0]:bbox[2], bbox[1]:bbox[3]], alpha=0.2, cmap='gray_r')   # of the form image_array[image_idx][y_min:y_max, x_min_x_max]

        plt.subplot(2, 1, 2)
        plt.imshow((RFP_image_array[image_idx]), cmap='gray')
        plt.imshow((intersection_masks_array[image_idx])[bbox[0]:bbox[2], bbox[1]:bbox[3]], alpha=0.2, cmap='gray_r')   # of the form image_array[image_idx][y_min:y_max, x_min_x_max]

        plt.show()


def main():
    # start_time = time.time()

    GFP_image_array = load_images("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\GFP\*.tif")
    RFP_image_array = load_images("L:\Julia_10March\Fish2\Timepoint1\Pos1\zStack\RFP\*.tif")

    GFP_masks_array = find_masks(GFP_image_array[160:163])
    RFP_masks_array = find_masks(RFP_image_array[160:163])

    intersection_masks_array = product_of_masks(GFP_masks_array, RFP_masks_array)
    
    bboxes = get_bounding_box(intersection_masks_array)
    print(bboxes)
    
    show_subset_image(GFP_image_array, RFP_image_array, intersection_masks_array, bboxes)

    
    
    # print("My program took ", time.time() - start_time, " seconds to run.")
    
    
    # np.savez_compressed('mask_finder_output.npz')

    # plt.figure()
    # plt.imshow(GFP_image_array[0], cmap='gray')

    # plt.figure()
    # plt.imshow(GFP_image_array[0], cmap='gray')
    # plt.imshow(GFP_masks_array[0], alpha=0.2, cmap='gray_r')
    


if __name__ == '__main__':
    main()


