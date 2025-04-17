import os
import cv2
import time

def capture_photo(save_directory="img", filename="photo.png"):
    # Create the directory if it does not exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Full path to the photo
    photo_path = os.path.join(save_directory, filename)

    # Initialize the camera (0 is usually the default camera on your system)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("Error: Camera not accessible. Check camera device.")
        return None

    # Wait for a short time to ensure the camera initializes
    time.sleep(0.1)

    # Capture a frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image. No frame captured.")
        cap.release()
        return None

    # Save the captured frame to the specified file
    cv2.imwrite(photo_path, frame)
    print(f"Photo captured and saved to {photo_path}")
    cap.release()
    return photo_path

capture_photo()