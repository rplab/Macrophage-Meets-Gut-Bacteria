# Macrophage-Meets-Gut-Bacteria
Python code for image analysis of the intersection of macrophages and gut bacteria. 

# Overarching Goals + Data Provided

The code for this project aims to identify and save images of instances where macrophages are clearly engulfing bacteria (intersection events) in the lumen of in transgenic mpeg-mcherry fish. The data that's run through the program are .tiff images from the folder Julia10_March, which contains images for 5 different fish, each of which have 13 timepoints and 4 regions.  The data from Julia_10_March is further split up into two channels: RFP and GFP. The RFP channel contains macrophages whereas the GFP channel contains vibrio-z20. 

The code for this program is split into two main Python files -- intersection_finder.py and display_intersection.py -- to make finding and saving intersections two distinct processes. An abbreivated summary for how both files work is provided below.


# Important Notes 

Please note that both intersection_finder.py and display_intersection.py only analyzs specific image slices and timepoints for all 5 fish in Julia10_March specified at the top of each file (also found at Timepoints & Z-Slices Used for Each Fish). Specific images slices are used because the fish is observed to have no clear intersection events for the first and last 100 or so images. Specific timepoints are used because the fish died prematurely during data collection, and we're not interested in analyzing data from an expired fish. For example, the image slices analyzed in Fish1 are slices 130-395 since it was clear by manual analysis that the first 130 and last 100 or so images didn't have any intersection events. Furthermore, only the first 5 timepoints are analyzed for Fish1 because Fish1 is dead from timepoints 5-13. 


# intersection_finder.py

intersection_finder.py loops through the data in Julia_10_March, applies appropriate thresholding criteria and filtering operations to the images, then creates and saves the resulting intersection mask arrays to a numpy compressed file if intersections are found. If no intersections are found for the specific fish, timepoint, and region, no intersection mask is created and the program skips to the next set of data. An intersection mask is produced for every 1 fish per 1 timepoint per 1 region and is saved to the folder intersection_mask_arrays, which is located in the same directory as the Julia10_March data folder. 

## main():

The majority of the work for identifying intersection events occurs in the main() function. main() loops through the data provided by Julia10_March in the following order: Fish, Timepoint, Pos (region). That means that the intersection mask arrays produced would be saved to the folder intersection_mask_arrays in the following order: Fish1-Timepoint1-Pos1, Fish1-Timepoint2-Pos1, Fish1-Timepoint3-Pos1, etc. (assuming that intersetions are found for these data). Regular expressions are utilzed to ensure that only desired image slices and timepoints are used for each fish (see section Important Notes above). For every fish, timepoint, and region, a GFP mask array and an RFP mask array is created. Then the resulting intersection mask array is produced by using the numpy logical_and function on the mask arrays for both channels. The intersection array is then saved to a numpy compressed file that's named with the appropriate fish number, timepoint number, and region number to which the original data came from (e.g Fish5-Timepoint12-Pos4). 

## find_threshold():

find_threshold() takes a single 2D image slice and returns its corresponding threshod using the formula threshold = median(image_slice) + 3 * standard deviation(image_slice).

## load_images_and_find_masks():

load_images_and_find_masks() first takes the name of the directory that holds the data for 1 fish, 1 timepoint, 1 region and the range of image slices analyzed for the fish. Next, the function 

1. reads each image slice in the directory
2. removes unncessary objects from the image using thresholding via the find_threshold() function
3. removes small objects from the image using the remove_small_objects function from the skimage.morphology module
4. fills any holes in the mask being produced using the binary_fill_holes function from the scipy.ndimage module
saves all of the resulting mask arays for the directory in a large 3D array


# display_intersection.py

display_intersection.py takes the numpy compressed files produced from intersection_finder.py, which are saved in the folder intersection_mask_arrays, displays the images using plots, and then saves them to a folder named intersection_images. 

## main():

main() loops through each of the intersection arrays in the folder intersection_mask_arrays, obtaining the corresponding fish number, timepoint number, and region number using regular expressions. The appropriate intersection mask array and image arrays for both GFP and RFP channels are loaded. The intersection mask is passed to the get_bounding_box function to get the bounding box for each intersection image slice. The bounding box, intersection mask array, GFP image array, RFP image array, and other information about the specific fish, timepoint, and region is then passed to the show_subset_image function to display the intersection events and save them to the folder intersection_images. 

## load_intersection_array():

load_intersection_array() takes in a numpy compressed file containing an array of intersection events and returns the corresponding loaded intersection mask array. 

## load_images():

load_images() loads a directory of images for either the GFP or RFP channel and returns the appropriate array of images.

## get_bounding_box():

The get_bounding_box function takes a loaded intersection mask array as input and returns a composite list of bounding boxes for each intersection image slice. The purpose of finding the bounding boxes of each intersection image slice is to provide a zoomed-in subplot of an intersection event in the show_subset_image function.

## show_subset_image():

show_subset_image takes in the following inputs:

- GFP_image_array: An array of images from a GFP channel
- RFP_image_array: An array of images from a RFP channel
- intersection_masks_array: An array of intersection masks
- intersection_bboxes: A list of intersection bounding boxes for the corresponding 1 Fish, 1 Timepoint, 1 Pos
- stack_indices: The desired image slices for the fish
- fish_number
- timepoint
- position (aka region)

For each of the bounding boxes in intersection_bboxes,  show_subset_image() calculates the maximum intensity projection of GFP_image_array, RFP_image_array, and intersection_masks_array along the z axis using the z-coordinates of each bounding box. Next, a 2x2 subplot is created, consisting of two types of subplots per channel. 

The first type of subplot that's created uses the maximum intensity projection of the original images for a particular channel (i.e GFP or RFP) and the maximum intensity projection of intersection_masks_array to clearly display the intersection mask overlaid on each channel; the coordinates of the current bounding box are used to draw a red box on the area where the intersection event is located for clarity.

The second type of subplot that's created is a zoomed-in image of the intersection event for the particular channel. That is, for the GFP channel, you would expect to see the pixels of the bacteria that were engulfed, whereas for the RFP channel, you would expect to see the macrophage that engulfed the bacteria. 

An example of an intersection image from Fish5-Timepoint3-Pos1 outputted from show_subset_image is show below. The top two images are subplots of the first type whereas the bottom two images are subplots of the second type. 

image_340-349.png

show_subset_image() stores the intersection images in the folder intersection_images so that each 1 Fish, 1 Timepoint, 1 Pos has its own folder. For example, if we wanted to find the intersection images for Fish5-Timepoint3-Pos1, we would navigate to the intersection_images folder, click on the Fish5-Timepoint3-Pos1 folder, and then view the images in the directory. 
 

Examples of Valid vs. Non-Valid Intersections 

Because intersection events are possible outside the lumen of transgenic mpeg-mcherry fish, a glance into any random folder inside intersection_images will often contain many intersections even though valid intersection events are rare. The number of total intersections in a folder can range from 12-70 images, with most containing 30-40 images. The number of valid intersections per folder average total around 2-3 intersections. Therefore, on average, users should expect approximately 5% of images in any given folder to contain valid intersections. Examples of both valid and non-valid intersections are provided below:


## VALID
Fish1-Timepoint1-Pos1-Slice295.png

image_294-296.png

Reason for Validity: As shown by the topmost image, the intersection event is clearly inside the lumen of the zebrafish. Furthermore, the corresponding maximum intensity projection image produced by the program clearly captures the shape of two bacterial cells that were engulfed by the macrophage. 


## NOT-VALID 


Example_outside_fish(not analyzed)-Fish4-Timepoint3-Pos1.png

Reason for Non-Validity: The macrophage depicted in the image above is outside the lumen and is merely engulfing autofloursecent cells. We know that the green specks in this image are not "real" bacterial cells because no aggregation is observed, which makes them autofluorescent cells. 


