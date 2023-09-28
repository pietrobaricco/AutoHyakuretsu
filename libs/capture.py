import cv2
import numpy as np


def capture_screen():
    import cv2
    import numpy as np
    from PIL import ImageGrab

    # Capture the screen as an RGB image
    screenshot = ImageGrab.grab().convert('RGB')

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
                if abs(center_x - match['x']) < 10 and abs(center_y - match['y']) < 10:
                    too_close = True
                    break

            # If the point is not too close to any previously stored point, add it to the match list
            if not too_close:
                match_info = {
                    "x": center_x,
                    "y": center_y,
                    # Add more information if needed
                }
                match_list.append(match_info)

        # Store the match list in the dictionary with the template name as the key
        template_matches[template.name] = match_list

    return template_matches
