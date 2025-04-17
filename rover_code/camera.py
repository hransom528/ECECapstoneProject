import os
import subprocess
import time

def capture_photo(save_directory="img", filename="photo.jpg"):
    # Create the directory if it does not exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Full path to the photo
    photo_path = os.path.join(save_directory, filename)

    # Run the v4l2-ctl command to capture an image from the camera
    try:
        command = f"v4l2-ctl --device=/dev/video1 --capture --filename={photo_path}"
        subprocess.run(command, shell=True, check=True)
        print(f"Photo captured and saved to {photo_path}")
        return photo_path
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

# Test the function
capture_photo()