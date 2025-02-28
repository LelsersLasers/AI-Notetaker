print("Starting...")

import shutil
from typing import Any

import argparse
import os
import json
import alive_progress
import pdf2image
import easyocr


"""
Features:
	- Input: slides (folder of pdfs) or video(s) (folder of videos or single video)
	- Output: notes or flashcards
	- Ask follow up questions
"""

# ---------------------------------------------------------------------------- #
NOTES_FILE = "notes.txt"
FLASHCARDS_FILE = "flashcards.txt"

TEMP_DIR = "temp"
TEMP_IMAGES = "images"
TEMP_DATA = "data_{i}.txt"

THROWAWAY = "Prof. Jeff Turkstra"
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
def setup_argparse() -> dict[str, Any]:
	# python main.py INPUT
	# -n, --notes = enable notes mode
	# -f, --flashcards = enable flashcards mode
	# -o, --output = output folder

	ap = argparse.ArgumentParser(description="Convert slides or videos to notes or flashcards")
	
	ap.add_argument("input", help="Input folder of slides or videos")
	ap.add_argument("-n", "--notes", help="Enable notes mode", action="store_true")
	ap.add_argument("-f", "--flashcards", help="Enable flashcards mode", action="store_true")
	ap.add_argument("-o", "--output", help="Output folder", default="output")

	args = vars(ap.parse_args())

	if not args["notes"] and not args["flashcards"]:
		raise Exception("No mode selected. Please select notes or flashcards mode")
	
	return args
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
def clear_temp() -> None:
	if os.path.exists(TEMP_DIR):
		print("Clearing temp directory...")
		shutil.rmtree(TEMP_DIR)	
# ---------------------------------------------------------------------------- #



# ---------------------------------------------------------------------------- #
def pdfs_to_images(pdfs_folder: str) -> None:
	# Convert PDFs to images
	print("Converting PDFs to images...")

	pdfs = sorted(os.listdir(pdfs_folder))

	if len(pdfs) == 0:
		raise Exception("No PDFs found in folder!")

	if not os.path.exists(TEMP_DIR):
		os.mkdir(TEMP_DIR)

	images_path = os.path.join(TEMP_DIR, TEMP_IMAGES)
	if not os.path.exists(images_path):
		os.mkdir(images_path)

	with alive_progress.alive_bar(len(pdfs), title="PDF -> Images") as bar:
		i_digits = len(str(len(pdfs) - 1))
		for i, pdf in enumerate(pdfs):
			pdf_path = os.path.join(pdfs_folder, pdf)
			images = pdf2image.convert_from_path(pdf_path)

			i_section = str(i).zfill(i_digits)

			j_digits = len(str(len(images) - 1))
			for j, image in enumerate(images):
				j_section = str(j).zfill(j_digits)
				image_path = os.path.join(images_path, f"{i_section}_{j_section}.jpg")
				image.save(str(image_path))
			
			bar()

# def alphabetize_images(images_folder: str) -> None:
# 	# Zero pad image names (sortable)
# 	print("Alphabetizing images...")

# 	images = os.listdir(images_folder)
# 	image_count = len(images)
# 	digits = len(str(image_count - 1))

# 	with alive_progress.alive_bar(image_count, title="Image name fixes") as bar:
# 		for image in images:
# 			# Uses the fact that files are named {i}.jpg
# 			i = int(image.split(".")[0])

# 			image_path = os.path.join(images_folder, image)
# 			new_image_path = os.path.join(images_folder, f"{str(i).zfill(digits)}.jpg")
# 			os.rename(image_path, new_image_path)
# 			bar()

def images_to_text(images_folder: str) -> None:
	# Convert images to text
	print("Converting images to text...")

	reader = easyocr.Reader(["en"])

	images = sorted(os.listdir(images_folder))

	# data_path = os.path.join(TEMP_DIR, TEMP_DATA)

	# with open(data_path, "w") as f:
	with alive_progress.alive_bar(len(images), title="Images -> text") as bar:
		for i, image in enumerate(images):
			file_name = TEMP_DATA.format(i=i)
			file_path = os.path.join(TEMP_DIR, file_name)
			with open(file_path, "a") as f:
				image_path = os.path.join(images_folder, image)
				text = reader.readtext(image_path, detail=0)

				if THROWAWAY in text:
					bar()
					continue

				# Names are: {i}_{j}.jpg where j is the slide number
				slide_number = int(image.split(".")[0].split("_")[1])
				output  = f"Slide {slide_number}:\n"
				output += "\n".join(text)
				output += "\n\n"
				f.write(output)

				bar()
# ---------------------------------------------------------------------------- #






# ---------------------------------------------------------------------------- #
def main() -> None:
	args = setup_argparse()

	clear_temp()

	pdfs_to_images(args["input"])
	# alphabetize_images(os.path.join(TEMP_DIR, TEMP_IMAGES))
	images_to_text(os.path.join(TEMP_DIR, TEMP_IMAGES))

	
main()
# ---------------------------------------------------------------------------- #




# PDFs only rn
# 1) PDFs -> images (pdf2image)
# 2) images -> text (EasyOCR)
# 3) images -> prompt("to text") -> text
# 4) Combine text
# 5) If notes mode, summarize text
# 6) If flashcards mode, extract key points

