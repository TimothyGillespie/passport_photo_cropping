from PIL import Image
import face_recognition
import os
import numpy as np
from sys import argv
from pathlib import Path

"""
This script is written to:
	- take a directory of pictures
	- crop the picture so it can fit a passphoto
	- save the picture in a specified output folder
"""

STANDARD_EXTENSIONS = ["jpg", "jpeg", "png"] #add to the list


def process_pictures(src_dir, dst_dir, ratio = (3,4) , free_space_ratio = 0.4, read_extensions = STANDARD_EXTENSIONS):
	"""
	Loads pictures from the source directory, crops the pictures and saves them to the destination directory.
	
	Args:
		src_dir (string): Relative or absolute path. The source directory which contains the pictures to be cropped.
		dst_dir (string): Relative or absolute path. The destination directory which is where the cropped pictures will be saved to.
		ratio ((int, int)): (Width,Height) The desired ratio of the cropped picture. (default: (3, 4))
		free_space_ratio (float): (Percentage total) The amount of empty space the cropped pic should achieve to the left and right. (default: 0.4 = 40%)
		read_extensions (array(string)): The picture extensions which should be read from the source directory. Other extensions will be ignored. (default see STANDARD_EXTENSIONS)

	Return:
	    void
	"""
	
	src_path = Path(src_dir)
	dst_path = Path(dst_dir)
	
	if not os.path.isdir(src_path):
		print("Error: {} is not a valid directory.".format(SRC_DIR))
		exit()
		
	if not os.path.isdir(dst_path):
		create_dir = input("{} does not exist yet. Do you wanna create this directory now? [Y/n]".format(dst_path))
		create_dir = create_dir.lower()
		if create_dir == "y" or create_dir == "":
			try:
				os.mkdir(dst_path)
			except:
				print("The directory couldn't be created. Does the path exist? Are the permission levels sufficient?")
				exit()
		else:
			print("Cannot continue without a destination directory")
			exit()

	src_dir_content = os.listdir(src_path)
	# Counts the number of successfully and unsuccessfully processed pictured
	success = fail = 0

	for picture in src_dir_content:
		picture_path = src_path / picture
		# Validating that it is a file with the allowed suffix
		if os.path.isfile(picture_path) and picture_path.suffix[1:] in read_extensions:
			picture_data = face_recognition.load_image_file(picture_path)
			features = face_recognition.face_landmarks(picture_data)
			if len(features) == 1:
				chin_positions = (features[0]["chin"])
				# Finding the edge of the chin 
				left, top = np.amin(chin_positions, axis=0)
				right, bottom = np.amax(chin_positions, axis = 0)
				face_width = right - left # in pixel
				face_percentage = 1.0 - free_space_ratio
				ppp_width = int(face_width / face_percentage) #ppp := passport photo
				side_extensions = int((ppp_width - face_width) / 2.0)
				left -= side_extensions
				right += side_extensions
				
				ppp_height = (ppp_width // ratio[0]) * ratio[1]
				below_chin_percentage = 0.11 # should be configurable
				bottom_extension = int(ppp_height * below_chin_percentage)
				top = int(bottom - (ppp_height * (1-below_chin_percentage)))
				bottom += bottom_extension
				
				if top < 0:
					top = 0
				if left < 0:
					left = 0
				
				###############################################################################
				# Insert handling for when the calculations will exceed the picture boundaries
				###############################################################################
				
				passport_photo = picture_data[top:bottom, left:right]
				pil_image = Image.fromarray(passport_photo)
				pil_image.save(dst_path / picture)
				success += 1
				print("Processed {} successfully.".format(picture))
				
			else:
				print("Could not process {}. Deteced none or more than one pictures.".format(picture_path))
				fail += 1
			print("{} picture(s) were succesfully processed. {} pictures were failed to process.".format(success, fail))
				

if __name__ == "__main__":
	# Variable set up
	try:
		SRC_DIR = argv[1]
		DST_DIR = argv[2]
	except IndexError:
		print("Error: Two arguments have to specified for the source and destination folder")
		exit()
		
	process_pictures(SRC_DIR, DST_DIR)