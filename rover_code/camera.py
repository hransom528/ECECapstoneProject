import os

def capture_photo(save_directory="img", filename="photo.jpg"):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    photo_path = os.path.join(save_directory, filename)

    cmd = f"fswebcam --no-banner -r 640x480 {photo_path}"
    result = os.system(cmd)

    if result == 0:
        print(f"Photo captured and saved to {photo_path}")
        return photo_path
    else:
        print("Error: Failed to capture image.")
        return None

def _manage_photo_count(directory, max_photos=3):
    """
    Ensures the number of photos in the directory does not exceed the specified max_photos.
    Deletes the oldest photo(s) if the count exceeds max_photos.
    Args:
        directory (str): Directory containing the photos.
        max_photos (int): Maximum number of photos to keep.
    """
    try:
        # Get all files in the directory sorted by creation time (oldest first)
        files = sorted(
            [os.path.join(directory, f) for f in os.listdir(directory)],
            key=os.path.getctime
        )

        # Check if the number of files exceeds the max_photos
        if len(files) > max_photos:
            # Calculate how many files to delete
            excess_files = len(files) - max_photos

            # Delete the oldest files
            for file_to_delete in files[:excess_files]:
                try:
                    os.remove(file_to_delete)
                    print(f"Deleted old photo: {file_to_delete}")
                except Exception as e:
                    print(f"Failed to delete {file_to_delete}: {e}")
    except Exception as e:
        print(f"Error managing photo count in directory '{directory}': {e}")

# capture_photo()