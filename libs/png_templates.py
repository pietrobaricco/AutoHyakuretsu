import json
import os

import cv2


class Template:
    # a template is a png file with some metadata attached
    # metadata can contain:
    # - a list of named relative x,y coordinates (from the top left corner of the template), each element is an object
    #   with the following properties:
    #   - x: the x coordinate
    #   - y: the y coordinate
    #   - name: the name of the coordinate

    # metadata is fetched on instantiation by parsing a .json file with the same name as the template but with .json
    # extension in the same folder, if it exists.

    def __init__(self, pngPath):
        self.pngPath = pngPath
        self.pngDir = os.path.dirname(pngPath)
        self.name = os.path.basename(pngPath).split(".")[0]
        self.metadata = self.get_metadata()

        # Load the template image (the image you want to search for)
        self.cv_template = cv2.imread(self.pngPath)
        # Get the dimensions of the template
        self.template_height, self.template_width, _ = self.cv_template.shape

        self.threshold = self.metadata["threshold"] if "threshold" in self.metadata else 0.9

    def get_metadata(self):
        metadata_file_path = self.pngDir + f"/{self.name}.json"
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, 'r') as metadata_file:
                return json.load(metadata_file)
        else:
            return []


def load_templates(folder_path):
    png_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.png')]
    ret = []
    for png_file in png_files:
        ret.append(Template(folder_path + "/" + png_file))
    return ret
