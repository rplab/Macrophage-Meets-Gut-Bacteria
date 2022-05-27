import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import imageio as io
from image_operations import sort_nicely
from skimage.morphology import remove_small_objects, binary_erosion, binary_opening
from scipy.ndimage import binary_fill_holes
from skimage.measure import label, regionprops

dir_GFP = glob("C:/Pos1_/Pos1/zStack/GFP/Default/*")
sort_nicely(dir_GFP)
dir_RFP = glob("C:/Pos1_/Pos1/zStack/RFP/Default/*")
sort_nicely(dir_RFP)

image_array_GFP = np.array([io.imread(i) for i in dir_GFP])
image_GFP = image_array_GFP[235]

image_array_RFP = np.array([io.imread(i) for i in dir_RFP])
image_RFP = image_array_RFP[235]

def find_threshold(array):
    median = np.median(array)
    std = np.std(array)
    threshold = median + 3 * std
    return threshold

mask_RFP = np.where(image_RFP<find_threshold(image_RFP), 0, 1)
bool_mask_RFP = np.array(mask_RFP, bool)
rm_RFP = remove_small_objects(bool_mask_RFP, 100, in_place=True) 
cleaned_mask_RFP = np.array(rm_RFP, int)

binary_opening(cleaned_mask_RFP)       # Remove noise
binary_fill_holes(cleaned_mask_RFP)    # Close any holes from image opening
smooth_mask_RFP = binary_erosion(cleaned_mask_RFP)

mask_GFP = np.where(image_GFP<find_threshold(image_GFP), 0, 1)
bool_mask_GFP = np.array(mask_GFP, bool)
rm_GFP = remove_small_objects(bool_mask_GFP, 100, in_place=True) 
cleaned_mask_GFP = np.array(rm_GFP, int)

binary_opening(cleaned_mask_GFP)       # Remove noise
binary_fill_holes(cleaned_mask_GFP)    # Close any holes from image opening
smooth_mask_GFP = binary_erosion(cleaned_mask_GFP)

# Determine if macrophages are close enough to bacteria
final_mask = np.logical_and(smooth_mask_RFP, smooth_mask_GFP)
labeled_mask = label(final_mask)
regions = regionprops(labeled_mask)

plt.figure()
plt.imshow(image_array_RFP[235][1:2048][600:])
plt.show()

### Display original vs. masked images for both channels ###
# plt.figure()
# plt.imshow(image_RFP, cmap='gray')

# plt.figure()
# plt.imshow(image_RFP, cmap='gray')
# plt.imshow(smooth_mask_RFP, alpha=0.2, cmap='gray_r')

# plt.figure()
# plt.imshow(image_GFP, cmap='gray')

# plt.figure()
# plt.imshow(image_GFP, cmap='gray')
# plt.imshow(smooth_mask_GFP, alpha=0.2, cmap='gray_r')

# plt.show()

