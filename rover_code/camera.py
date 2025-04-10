import cv2
import os
# from datetime import datetime

def capture_photo(save_directory="img", filename="photo.jpg"):
    """
    Captures a single photo using the Raspberry Pi camera and saves it to a file.
    Ensures no more than 3 photos are kept in the directory by deleting the oldest one.
    Args:
        save_directory (str): Directory where the photo will be saved.
    Returns:
        str: Path to the saved photo, or None if an error occurs.
    """
    # Ensure the save directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Manage photo count in the save directory
    # _manage_photo_count(save_directory, max_photos=3)

    # Generate a timestamped filename
    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # photo_path = os.path.join(save_directory, f"photo_{timestamp}.jpg")
    photo_path = os.path.join(save_directory, f"photo.jpg")

    # Open the camera
    camera = cv2.VideoCapture(0)  # 0 is the index for the first camera

    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return None

    try:
        # Capture a single frame
        ret, frame = camera.read()

        if not ret:
            print("Error: Failed to capture image.")
            return None

        # Save the captured frame as an image file
        cv2.imwrite(photo_path, frame)
        print(f"Photo captured and saved to {photo_path}")
        return photo_path

    except Exception as e:
        print(f"Error during photo capture: {e}")
        return None

    finally:
        # Release the camera
        camera.release()

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