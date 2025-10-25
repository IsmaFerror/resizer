# resizer
Image Downloader and Resizer

This is a simple Python script designed to download a list of images from URLs. It resizes each image to a uniform size (e.g., 250x400), centers it, and saves it as a PNG file with a transparent background.

Features

Download from URLs: Fetches images from the web using the requests library.

Uniform Resizing: Resizes all images to a specified FINAL_SIZE.

Maintains Aspect Ratio: Uses Pillow's thumbnail method to resize without distorting the image.

Transparent Background: Pastes the resized image onto a transparent canvas of the final size.

PNG Optimization: Saves images in an optimized PNG format.

Safe Filenames: Sanitizes image names to create valid filenames.

Requirements

Python 3.x

requests library

Pillow (PIL) library

You can install the necessary dependencies using pip:

pip install requests pillow


How to Use

1. Populate the images Dictionary

The most important step is to edit the .py file and fill in the images dictionary. You must provide a name for the image and the direct URL to the image.

The script includes the Python logo as a placeholder. You can add as many images as you need.

Example of how to fill it:

# --- CONFIG ---
OUTPUT_DIR = "output"
FINAL_SIZE = (250, 400)
# ...
# ---------------

# Dictionary: name → URL (or path) of the image
# example:
images = {
    "Python_logo": "[https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png)",
    "My_Awesome_Image": "[https://your-url-here.com/image.jpg](https://your-url-here.com/image.jpg)",
    # ... Add all the images you need here
}

# ... (rest of the script)


2. (Optional) Adjust Configuration

You can change the following variables in the --- CONFIG --- section of the script:

OUTPUT_DIR: The name of the directory where the processed images will be saved (default: "output").

FINAL_SIZE: A tuple (width, height) in pixels for the final size of all images (default: (250, 400)).

TIMEOUT: Maximum time in seconds to wait for the download response (default: 15).

3. Run the Script

Once you have populated the images dictionary and adjusted the configuration, save the file (e.g., as download_and_resize.py) and run it from your terminal:

python3 download_and_resize.py


The script will display the progress in the terminal (note: the script's output is in Spanish, as provided in the code):

Procesando carta: Python_logo
   Guardada: output/Python_logo.png
Procesando carta: My_Awesome_Image
   Guardada: output/My_Awesome_Image.png
...
Completadas: 2/2


4. Check the Results

The final images will be in the output directory you specified (default: output/).

File Structure

your-project/
│
├── download_and_resize.py   <-- (Your edited script)
│
└── output/                  <-- (Directory created by the script)
    ├── Python_logo.png
    ├── My_Awesome_Image.png
    └── ...
