import logging
import os
import tempfile

import cv2
import numpy as np
import tesserocr
from PIL import Image

from libs.delay import NonBlockingDelay


def capture_screen(bbox=None, delay_ms=0):
    import cv2
    import numpy as np
    from PIL import ImageGrab

    if delay_ms > 0:
        NonBlockingDelay.wait(delay_ms)

    # Capture the screen as an RGB image
    screenshot = ImageGrab.grab(bbox=bbox).convert('RGB')

    # Convert the RGB image (PIL Image) to a NumPy array
    screenshot_np = np.array(screenshot)

    # Convert the NumPy array from RGB to BGR format
    bgr_image = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Now, 'bgr_image' contains the screen capture in BGR format, which is the format used by OpenCV.
    return bgr_image


def get_matches(templates, screenshot_cv):
    # Initialize a dictionary to store the matches
    template_matches = {}

    # Iterate over the templates
    for template in templates:

        # Perform template matching
        result = cv2.matchTemplate(screenshot_cv, template.cv_template, cv2.TM_CCOEFF_NORMED)

        # Find locations where the match exceeds a certain threshold
        threshold = template.threshold  # Adjust this threshold as needed

        loc = np.where(result >= threshold)

        # Initialize a list to store match information
        match_list = []

        # Iterate over the found locations and store match information
        for pt in zip(*loc[::-1]):
            center_x = pt[0] + template.template_width // 2
            center_y = pt[1] + template.template_height // 2

            # Check if this point is at least 5 pixels away from all previously stored points
            too_close = False
            for match in match_list:
                if abs(center_x - match['center_x']) < 10 and abs(center_y - match['center_y']) < 10:
                    too_close = True
                    break

            # If the point is not too close to any previously stored point, add it to the match list
            if not too_close:
                match_info = {
                    "center_x": center_x,
                    "center_y": center_y,
                    "x": pt[0],
                    "y": pt[1],
                    # Add more information if needed
                }
                match_list.append(match_info)

        # Store the match list in the dictionary with the template name as the key
        template_matches[template.name] = match_list

    return template_matches

class ocr_utils:

    def __init__(self, app):
        self.app = app
        self.apis = {}

    def ocr(self, cv_image, x=0, y=0, w=0, h=0, psm=6, threshold=80):
        #api.SetVariable('load_system_dawg', 'false')
        #api.SetVariable('load_freq_dawg', 'false')

        api = self.apis.get(psm, None)
        if api is None:
            api = tesserocr.PyTessBaseAPI(psm=psm)  # Use psm=6 for multiline text
            self.apis[psm] = api

        # Crop the image based on the specified coordinates and dimensions
        cropped = cv_image[y:y + h, x: x + w]
        # Convert the cropped image to grayscale
        img2gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        # if the vertical resolution is too low, we need to upscale the image
        if img2gray.shape[0] < 50:
            original_level = logging.getLogger().getEffectiveLevel()
            # Set the logging level to suppress messages (e.g., WARNING)
            logging.getLogger().setLevel(logging.WARNING)
            # Code where you want to suppress log messages
            img2gray = self.app.image_manipulator.upscale_gray_4x(img2gray)
            # Restore the original logging level
            logging.getLogger().setLevel(original_level)

        if(threshold != 0):
            # Apply adaptive thresholding to create a binary image
            _, thresholded = cv2.threshold(img2gray, threshold, 255, cv2.THRESH_BINARY)
            _, inverted_thresholded = cv2.threshold(img2gray, threshold, 255, cv2.THRESH_BINARY_INV)
        else:
            thresholded = img2gray
            inverted_thresholded = img2gray


        # Create a PIL Image from the thresholded image
        im_pil = Image.fromarray(thresholded)

        # Set the image for OCR processing
        api.SetImage(im_pil)

        # Perform OCR on the image with line breaks
        ocred_text = api.GetUTF8Text()

        # Get confidence scores for individual words (optional)
        confidence = api.AllWordConfidences()
        confidence = confidence[0] if len(confidence) >= 1 else -1

        # make the same for inverted image
        im_pil = Image.fromarray(inverted_thresholded)
        api.SetImage(im_pil)
        ocred_text_inv = api.GetUTF8Text()
        confidence_inv = api.AllWordConfidences()
        confidence_inv = confidence_inv[0] if len(confidence_inv) >= 1 else -1

        # Return the best result
        if confidence > confidence_inv:
            return ocred_text, confidence
        else:
            return ocred_text_inv, confidence_inv